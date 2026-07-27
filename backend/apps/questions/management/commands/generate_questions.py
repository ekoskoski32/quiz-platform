"""
Management command to generate quiz questions using GPT-4o.

Usage:
    python manage.py generate_questions
    python manage.py generate_questions --clear        # wipe existing first
    python manage.py generate_questions --per-category 20
    python manage.py generate_questions --categories "Math,Science"
"""
import json
import os
import time

from django.core.management.base import BaseCommand

from apps.questions.models import Choice, Question

CATEGORIES = [
    "Geography",
    "Science",
    "Math",
    "History",
    "Technology",
    "Biology",
    "Art",
    "Pop Culture",
]

SYSTEM_PROMPT = """You are a quiz question generator. Generate diverse, accurate quiz questions.

CRITICAL: Return a JSON object with a single key "questions" containing an array of question objects.

Each question object MUST use EXACTLY these field names:
- "type": MUST be one of exactly: "single", "multiple", "numerical", "text", "image"
- "prompt": the question text (NOT "question", NOT "q")
- "difficulty": MUST be exactly: "easy", "medium", or "hard"
- "correct_answer": string — required for "text" and "numerical" types, omit for others
- "choices": array — required for "single" and "multiple" types only
  - each choice: {"text": string, "is_correct": boolean}

TYPE RULES (strictly follow these):
- "single": exactly one choice has is_correct=true, provide 4 choices total
- "multiple": 2 or more choices have is_correct=true, provide 4-5 choices total
- "numerical": correct_answer is a number as a string e.g. "42" or "3.14"
- "text": correct_answer is a model answer in 1-2 sentences
- "image": prompt tells user what to photograph or draw, correct_answer describes what correct image shows

Mix difficulties: ~40% easy, 40% medium, 20% hard.
Include all 5 types across the batch.
Make questions educational and interesting.

EXAMPLE of correct format:
{
  "questions": [
    {
      "type": "single",
      "prompt": "What is the capital of Japan?",
      "difficulty": "easy",
      "choices": [
        {"text": "Beijing", "is_correct": false},
        {"text": "Tokyo", "is_correct": true},
        {"text": "Seoul", "is_correct": false},
        {"text": "Bangkok", "is_correct": false}
      ]
    },
    {
      "type": "numerical",
      "prompt": "How many sides does a hexagon have?",
      "difficulty": "easy",
      "correct_answer": "6"
    },
    {
      "type": "text",
      "prompt": "What is the greenhouse effect?",
      "difficulty": "medium",
      "correct_answer": "The greenhouse effect is when gases in Earth's atmosphere trap heat from the sun, warming the planet's surface."
    }
  ]
}
"""


def generate_batch(client, category: str, count: int, existing_prompts: list) -> list:
    """Ask GPT-4o to generate `count` questions for a given category."""
    avoid = ""
    if existing_prompts:
        sample = existing_prompts[:10]
        avoid = f"\n\nAvoid questions similar to these already in the bank:\n" + "\n".join(f"- {p}" for p in sample)

    user_msg = (
        f"Generate {count} quiz questions for the category: {category}\n"
        f"Include a mix of all 5 types: single, multiple, numerical, text, image.{avoid}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    # GPT-4o with json_object always returns a dict — unwrap the array
    if isinstance(data, dict):
        # Try known keys first
        for key in ("questions", "items", "data", "results", "quiz_questions", "question_bank"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # Try any value that's a list
        for val in data.values():
            if isinstance(val, list) and len(val) > 0:
                return val
        return []

    return data if isinstance(data, list) else []


def save_question(category: str, q_data: dict) -> bool:
    """Validate and save one question. Returns True if saved."""
    q_type = q_data.get("type")
    prompt = q_data.get("prompt", "").strip()
    difficulty = q_data.get("difficulty", "medium")
    correct_answer = str(q_data.get("correct_answer", "")).strip()
    choices = q_data.get("choices", [])

    if not prompt or q_type not in ("single", "multiple", "numerical", "text", "image"):
        return False

    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"

    # Validate per type
    if q_type == "single":
        correct = [c for c in choices if c.get("is_correct")]
        if len(correct) != 1 or len(choices) < 3:
            return False
    elif q_type == "multiple":
        correct = [c for c in choices if c.get("is_correct")]
        if len(correct) < 2:
            return False
    elif q_type == "numerical":
        try:
            float(correct_answer)
        except (ValueError, TypeError):
            return False
    elif q_type == "text":
        if not correct_answer:
            return False

    question = Question.objects.create(
        type=q_type,
        prompt=prompt,
        category=category,
        difficulty=difficulty,
        correct_answer=correct_answer if q_type in ("text", "numerical") else "",
    )

    for choice in choices:
        text = str(choice.get("text", "")).strip()
        is_correct = bool(choice.get("is_correct", False))
        if text:
            Choice.objects.create(question=question, text=text, is_correct=is_correct)

    return True


class Command(BaseCommand):
    help = "Generate quiz questions using GPT-4o"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing questions before generating",
        )
        parser.add_argument(
            "--per-category",
            type=int,
            default=20,
            dest="per_category",
            help="Number of questions to generate per category (default: 20)",
        )
        parser.add_argument(
            "--categories",
            type=str,
            default="",
            help="Comma-separated list of categories (default: all)",
        )

    def handle(self, *args, **options):
        import openai
        api_key = os.getenv("OPENAI_API_KEY", "stub")
        if api_key == "stub" or not api_key.startswith("sk-"):
            self.stderr.write(self.style.ERROR(
                "OPENAI_API_KEY not set. Add it to backend/.env"
            ))
            return

        client = openai.OpenAI(api_key=api_key)

        if options["clear"]:
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing questions."))

        categories = (
            [c.strip() for c in options["categories"].split(",") if c.strip()]
            if options["categories"]
            else CATEGORIES
        )
        per_category = options["per_category"]
        total_saved = 0

        for category in categories:
            self.stdout.write(f"\n→ Generating {per_category} questions for: {category}")

            # Get existing prompts to avoid duplicates
            existing = list(
                Question.objects.filter(category=category)
                .values_list("prompt", flat=True)
            )

            saved = 0
            attempts = 0
            max_attempts = 3

            while saved < per_category and attempts < max_attempts:
                needed = per_category - saved
                # Request a bit extra to account for validation failures
                batch_size = min(needed + 3, 10)

                try:
                    self.stdout.write(f"  Batch {attempts + 1}: requesting {batch_size} questions...")
                    questions = generate_batch(client, category, batch_size, existing)
                    self.stdout.write(f"  Received {len(questions)} questions from GPT-4o")

                    for q in questions:
                        if saved >= per_category:
                            break
                        if save_question(category, q):
                            saved += 1
                            existing.append(q.get("prompt", ""))
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"  Skipped invalid: {q.get('prompt', '')[:50]}")
                            )

                    attempts += 1
                    if saved < per_category and attempts < max_attempts:
                        time.sleep(1)  # brief pause between retries

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  Error: {e}"))
                    attempts += 1
                    time.sleep(2)

            self.stdout.write(
                self.style.SUCCESS(f"  ✓ Saved {saved}/{per_category} questions for {category}")
            )
            total_saved += saved

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Done. Generated {total_saved} questions total.")
        )
        self.stdout.write(
            f"  Total in bank: {Question.objects.count()} questions"
        )
