"""
Grading logic for quiz answers.

Auto-grading:  single choice, multiple choice, numerical — immediate, deterministic.
AI grading:    text → GPT-4o semantic comparison
               image → GPT-4o Vision evaluates the upload against the question requirement
"""
import json
import os


def grade_answer(answer) -> dict:
    """
    Grade a single Answer instance.
    Returns {"is_correct": bool|None, "ai_feedback": str}
    """
    q = answer.question

    if q.type == "single":
        selected = answer.selected_choices.first()
        correct = selected is not None and selected.is_correct
        return {"is_correct": correct, "ai_feedback": ""}

    elif q.type == "multiple":
        correct_ids = set(q.choices.filter(is_correct=True).values_list("id", flat=True))
        selected_ids = set(answer.selected_choices.values_list("id", flat=True))
        return {"is_correct": correct_ids == selected_ids, "ai_feedback": ""}

    elif q.type == "numerical":
        try:
            user_val = float(answer.text_response.strip())
            correct_val = float(q.correct_answer.strip())
            return {"is_correct": abs(user_val - correct_val) < 1e-9, "ai_feedback": ""}
        except (ValueError, AttributeError):
            return {"is_correct": False, "ai_feedback": ""}

    elif q.type == "text":
        return _grade_text(q.prompt, q.correct_answer, answer.text_response)

    elif q.type == "image":
        if not answer.image_response:
            return {"is_correct": False, "ai_feedback": "No image uploaded."}
        return _grade_image(q.prompt, answer.image_response.path)

    return {"is_correct": False, "ai_feedback": ""}


def _get_client():
    import openai
    api_key = os.getenv("OPENAI_API_KEY", "stub")
    if api_key == "stub" or not api_key.startswith("sk-"):
        return None, api_key
    return openai.OpenAI(api_key=api_key), api_key


def _grade_text(prompt: str, correct_answer: str, user_answer: str) -> dict:
    client, api_key = _get_client()

    if client is None:
        # Stub: keyword overlap heuristic
        user_words = set(user_answer.lower().split())
        correct_words = set(correct_answer.lower().split())
        overlap = len(user_words & correct_words) / max(len(correct_words), 1)
        return {
            "is_correct": overlap >= 0.4,
            "ai_feedback": "[Stub grading] Your answer partially matches the model answer.",
        }

    try:
        system_msg = (
            "You are a quiz grader. Given a question, a model answer, and a "
            "student response, decide if the student answer is essentially correct. "
            "Be generous with wording but strict on facts. "
            'Reply ONLY with valid JSON: {"is_correct": true/false, "feedback": "..."}'
        )
        user_msg = (
            f"Question: {prompt}\n"
            f"Model answer: {correct_answer}\n"
            f"Student answer: {user_answer}"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "is_correct": bool(result.get("is_correct")),
            "ai_feedback": result.get("feedback", ""),
        }
    except Exception as e:
        return {"is_correct": None, "ai_feedback": f"Grading error: {e}"}


def _grade_image(prompt: str, image_path: str) -> dict:
    client, api_key = _get_client()

    if client is None:
        return {
            "is_correct": None,
            "ai_feedback": "Image submitted — pending admin review.",
        }

    try:
        import base64
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        prompt_text = (
            f"Quiz question: {prompt}\n"
            "Does the uploaded image fulfill the requirement described in the question? "
            'Reply ONLY with valid JSON: {"is_correct": true/false, "feedback": "..."}'
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "is_correct": bool(result.get("is_correct")),
            "ai_feedback": result.get("feedback", ""),
        }
    except Exception as e:
        return {"is_correct": None, "ai_feedback": f"Image grading error: {e}"}
