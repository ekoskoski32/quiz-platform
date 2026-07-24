"""
Django management command to seed the question bank with 25 sample questions.

Usage:
    python manage.py seed
    python manage.py seed --clear   (wipe existing questions first)
"""
from django.core.management.base import BaseCommand
from apps.questions.models import Choice, Question

QUESTIONS = [
    # ── Single Choice (6 questions) ──────────────────────────────────────────
    {
        "type": "single", "category": "Geography", "difficulty": "easy",
        "prompt": "What is the capital of France?",
        "choices": [
            {"text": "Berlin", "is_correct": False},
            {"text": "Paris", "is_correct": True},
            {"text": "Madrid", "is_correct": False},
            {"text": "Rome", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Science", "difficulty": "easy",
        "prompt": "What planet is closest to the Sun?",
        "choices": [
            {"text": "Venus", "is_correct": False},
            {"text": "Earth", "is_correct": False},
            {"text": "Mercury", "is_correct": True},
            {"text": "Mars", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "History", "difficulty": "medium",
        "prompt": "In what year did World War II end?",
        "choices": [
            {"text": "1943", "is_correct": False},
            {"text": "1944", "is_correct": False},
            {"text": "1945", "is_correct": True},
            {"text": "1946", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Technology", "difficulty": "medium",
        "prompt": "Which company created the Python programming language?",
        "choices": [
            {"text": "Google", "is_correct": False},
            {"text": "Microsoft", "is_correct": False},
            {"text": "Guido van Rossum / CWI", "is_correct": True},
            {"text": "Apple", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Science", "difficulty": "hard",
        "prompt": "What is the chemical symbol for Gold?",
        "choices": [
            {"text": "Go", "is_correct": False},
            {"text": "Gd", "is_correct": False},
            {"text": "Au", "is_correct": True},
            {"text": "Ag", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Pop Culture", "difficulty": "easy",
        "prompt": "Who painted the Mona Lisa?",
        "choices": [
            {"text": "Michelangelo", "is_correct": False},
            {"text": "Raphael", "is_correct": False},
            {"text": "Leonardo da Vinci", "is_correct": True},
            {"text": "Caravaggio", "is_correct": False},
        ],
    },
    # ── Multiple Choice (6 questions) ────────────────────────────────────────
    {
        "type": "multiple", "category": "Math", "difficulty": "medium",
        "prompt": "Which of the following are prime numbers?",
        "choices": [
            {"text": "2", "is_correct": True},
            {"text": "4", "is_correct": False},
            {"text": "7", "is_correct": True},
            {"text": "9", "is_correct": False},
            {"text": "11", "is_correct": True},
        ],
    },
    {
        "type": "multiple", "category": "Science", "difficulty": "medium",
        "prompt": "Which of the following are planets in our solar system?",
        "choices": [
            {"text": "Mars", "is_correct": True},
            {"text": "Pluto", "is_correct": False},
            {"text": "Neptune", "is_correct": True},
            {"text": "Europa", "is_correct": False},
            {"text": "Saturn", "is_correct": True},
        ],
    },
    {
        "type": "multiple", "category": "Technology", "difficulty": "easy",
        "prompt": "Which of the following are programming languages?",
        "choices": [
            {"text": "Python", "is_correct": True},
            {"text": "HTML", "is_correct": False},
            {"text": "JavaScript", "is_correct": True},
            {"text": "SQL", "is_correct": False},
            {"text": "Rust", "is_correct": True},
        ],
    },
    {
        "type": "multiple", "category": "History", "difficulty": "hard",
        "prompt": "Which countries were part of the Allied Powers in World War II?",
        "choices": [
            {"text": "United States", "is_correct": True},
            {"text": "Germany", "is_correct": False},
            {"text": "United Kingdom", "is_correct": True},
            {"text": "Japan", "is_correct": False},
            {"text": "Soviet Union", "is_correct": True},
        ],
    },
    {
        "type": "multiple", "category": "Biology", "difficulty": "medium",
        "prompt": "Which of the following are organs in the human body?",
        "choices": [
            {"text": "Heart", "is_correct": True},
            {"text": "Femur", "is_correct": False},
            {"text": "Liver", "is_correct": True},
            {"text": "Bicep", "is_correct": False},
            {"text": "Kidney", "is_correct": True},
        ],
    },
    {
        "type": "multiple", "category": "Geography", "difficulty": "easy",
        "prompt": "Which of the following are continents?",
        "choices": [
            {"text": "Africa", "is_correct": True},
            {"text": "Atlantic", "is_correct": False},
            {"text": "Asia", "is_correct": True},
            {"text": "Sahara", "is_correct": False},
            {"text": "Australia", "is_correct": True},
        ],
    },
    # ── Numerical (5 questions) ───────────────────────────────────────────────
    {
        "type": "numerical", "category": "Math", "difficulty": "easy",
        "prompt": "How many degrees are in a right angle?",
        "correct_answer": "90",
    },
    {
        "type": "numerical", "category": "Science", "difficulty": "easy",
        "prompt": "How many bones are in the adult human body?",
        "correct_answer": "206",
    },
    {
        "type": "numerical", "category": "Math", "difficulty": "medium",
        "prompt": "What is 15 squared (15²)?",
        "correct_answer": "225",
    },
    {
        "type": "numerical", "category": "Science", "difficulty": "medium",
        "prompt": "At what temperature (°C) does water boil at sea level?",
        "correct_answer": "100",
    },
    {
        "type": "numerical", "category": "History", "difficulty": "hard",
        "prompt": "In what year was the United States Declaration of Independence signed?",
        "correct_answer": "1776",
    },
    # ── Text / Free Response (4 questions) ───────────────────────────────────
    {
        "type": "text", "category": "Biology", "difficulty": "medium",
        "prompt": "In one sentence, what is photosynthesis?",
        "correct_answer": "The process by which plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
    },
    {
        "type": "text", "category": "Technology", "difficulty": "easy",
        "prompt": "What does HTML stand for?",
        "correct_answer": "HyperText Markup Language",
    },
    {
        "type": "text", "category": "Science", "difficulty": "hard",
        "prompt": "What is Newton's Second Law of Motion?",
        "correct_answer": "Force equals mass times acceleration (F = ma).",
    },
    {
        "type": "text", "category": "History", "difficulty": "medium",
        "prompt": "Who was the first President of the United States?",
        "correct_answer": "George Washington",
    },
    # ── Image Upload (4 questions) ────────────────────────────────────────────
    {
        "type": "image", "category": "Biology", "difficulty": "easy",
        "prompt": "Upload a photo of any green plant.",
        "correct_answer": "A photo showing a green plant.",
    },
    {
        "type": "image", "category": "Art", "difficulty": "easy",
        "prompt": "Draw or photograph something that represents the color blue.",
        "correct_answer": "An image prominently featuring the color blue.",
    },
    {
        "type": "image", "category": "Math", "difficulty": "medium",
        "prompt": "Write the number '42' on paper and upload a photo of it.",
        "correct_answer": "A handwritten or printed '42'.",
    },
    {
        "type": "image", "category": "Science", "difficulty": "hard",
        "prompt": "Draw the water cycle and upload a photo of your drawing.",
        "correct_answer": "A diagram showing evaporation, condensation, and precipitation.",
    },
    {
        "type": "image", "category": "Pop Culture", "difficulty": "easy",
        "prompt": "Take a photo of something in your surroundings that is circular.",
        "correct_answer": "A photo of a circular object.",
    },
    # ── Extra questions (ensure all categories have ≥5) ───────────────────────
    {
        "type": "single", "category": "History", "difficulty": "easy",
        "prompt": "Who was the first President of the United States?",
        "choices": [
            {"text": "Thomas Jefferson", "is_correct": False},
            {"text": "George Washington", "is_correct": True},
            {"text": "Abraham Lincoln", "is_correct": False},
            {"text": "John Adams", "is_correct": False},
        ],
    },
    {
        "type": "multiple", "category": "History", "difficulty": "hard",
        "prompt": "Which of the following were ancient wonders of the world?",
        "choices": [
            {"text": "The Great Pyramid of Giza", "is_correct": True},
            {"text": "The Colosseum", "is_correct": False},
            {"text": "The Hanging Gardens of Babylon", "is_correct": True},
            {"text": "The Great Wall of China", "is_correct": False},
            {"text": "The Statue of Zeus at Olympia", "is_correct": True},
        ],
    },
    {
        "type": "text", "category": "History", "difficulty": "medium",
        "prompt": "What event triggered the start of World War I?",
        "correct_answer": "The assassination of Archduke Franz Ferdinand of Austria in Sarajevo in 1914.",
    },
    {
        "type": "single", "category": "Geography", "difficulty": "medium",
        "prompt": "What is the longest river in the world?",
        "choices": [
            {"text": "Amazon", "is_correct": False},
            {"text": "Yangtze", "is_correct": False},
            {"text": "Nile", "is_correct": True},
            {"text": "Mississippi", "is_correct": False},
        ],
    },
    {
        "type": "numerical", "category": "Geography", "difficulty": "hard",
        "prompt": "How many countries are in the United Nations (as of 2024)?",
        "correct_answer": "193",
    },
    {
        "type": "single", "category": "Geography", "difficulty": "easy",
        "prompt": "What is the smallest country in the world by area?",
        "choices": [
            {"text": "Monaco", "is_correct": False},
            {"text": "San Marino", "is_correct": False},
            {"text": "Vatican City", "is_correct": True},
            {"text": "Liechtenstein", "is_correct": False},
        ],
    },
    {
        "type": "text", "category": "Art", "difficulty": "medium",
        "prompt": "What art movement is Salvador Dali associated with?",
        "correct_answer": "Surrealism",
    },
    {
        "type": "single", "category": "Art", "difficulty": "easy",
        "prompt": "In what museum is the Mona Lisa displayed?",
        "choices": [
            {"text": "The Louvre", "is_correct": True},
            {"text": "The Metropolitan Museum of Art", "is_correct": False},
            {"text": "The Uffizi Gallery", "is_correct": False},
            {"text": "The Prado", "is_correct": False},
        ],
    },
    {
        "type": "numerical", "category": "Art", "difficulty": "hard",
        "prompt": "In what year did Vincent van Gogh paint Starry Night?",
        "correct_answer": "1889",
    },
    {
        "type": "multiple", "category": "Art", "difficulty": "medium",
        "prompt": "Which of the following are Impressionist painters?",
        "choices": [
            {"text": "Claude Monet", "is_correct": True},
            {"text": "Pablo Picasso", "is_correct": False},
            {"text": "Pierre-Auguste Renoir", "is_correct": True},
            {"text": "Michelangelo", "is_correct": False},
            {"text": "Edgar Degas", "is_correct": True},
        ],
    },
    {
        "type": "single", "category": "Pop Culture", "difficulty": "easy",
        "prompt": "Which band released the album Abbey Road?",
        "choices": [
            {"text": "The Rolling Stones", "is_correct": False},
            {"text": "The Beatles", "is_correct": True},
            {"text": "Led Zeppelin", "is_correct": False},
            {"text": "Pink Floyd", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Pop Culture", "difficulty": "medium",
        "prompt": "Which movie won the first Academy Award for Best Picture?",
        "choices": [
            {"text": "Gone with the Wind", "is_correct": False},
            {"text": "Casablanca", "is_correct": False},
            {"text": "Wings", "is_correct": True},
            {"text": "Sunrise", "is_correct": False},
        ],
    },
    {
        "type": "text", "category": "Pop Culture", "difficulty": "easy",
        "prompt": "What is the name of Tony Stark's AI assistant in the Iron Man films?",
        "correct_answer": "JARVIS",
    },
    # ── Math top-up (need 1 more → total 5) ──────────────────────────────────
    {
        "type": "single", "category": "Math", "difficulty": "easy",
        "prompt": "What is the value of pi rounded to two decimal places?",
        "choices": [
            {"text": "3.12", "is_correct": False},
            {"text": "3.14", "is_correct": True},
            {"text": "3.16", "is_correct": False},
            {"text": "3.18", "is_correct": False},
        ],
    },
    {
        "type": "single", "category": "Math", "difficulty": "medium",
        "prompt": "What is the square root of 144?",
        "choices": [
            {"text": "10", "is_correct": False},
            {"text": "11", "is_correct": False},
            {"text": "12", "is_correct": True},
            {"text": "14", "is_correct": False},
        ],
    },
    {
        "type": "text", "category": "Math", "difficulty": "hard",
        "prompt": "What is the difference between mean, median, and mode?",
        "correct_answer": "Mean is the average of all values; median is the middle value when sorted; mode is the most frequently occurring value.",
    },
    # ── Biology top-up (need 2 more → total 5) ───────────────────────────────
    {
        "type": "single", "category": "Biology", "difficulty": "easy",
        "prompt": "What is the powerhouse of the cell?",
        "choices": [
            {"text": "Nucleus", "is_correct": False},
            {"text": "Ribosome", "is_correct": False},
            {"text": "Mitochondria", "is_correct": True},
            {"text": "Golgi apparatus", "is_correct": False},
        ],
    },
    {
        "type": "multiple", "category": "Biology", "difficulty": "medium",
        "prompt": "Which of the following are types of blood cells?",
        "choices": [
            {"text": "Red blood cells", "is_correct": True},
            {"text": "White blood cells", "is_correct": True},
            {"text": "Platelets", "is_correct": True},
            {"text": "Plasma cells", "is_correct": False},
        ],
    },
    {
        "type": "numerical", "category": "Biology", "difficulty": "hard",
        "prompt": "How many pairs of chromosomes does a typical human cell contain?",
        "correct_answer": "23",
    },
    # ── Technology top-up (need 2 more → total 5) ────────────────────────────
    {
        "type": "single", "category": "Technology", "difficulty": "easy",
        "prompt": "What does CPU stand for?",
        "choices": [
            {"text": "Central Processing Unit", "is_correct": True},
            {"text": "Central Power Unit", "is_correct": False},
            {"text": "Computer Processing Unit", "is_correct": False},
            {"text": "Core Processing Unit", "is_correct": False},
        ],
    },
    {
        "type": "multiple", "category": "Technology", "difficulty": "medium",
        "prompt": "Which of the following are cloud computing providers?",
        "choices": [
            {"text": "AWS", "is_correct": True},
            {"text": "Google Cloud", "is_correct": True},
            {"text": "Microsoft Azure", "is_correct": True},
            {"text": "Oracle Financials", "is_correct": False},
        ],
    },
    {
        "type": "text", "category": "Technology", "difficulty": "hard",
        "prompt": "What does REST stand for in REST API?",
        "correct_answer": "Representational State Transfer",
    },
]


class Command(BaseCommand):
    help = "Seed the question bank with 25 sample questions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing questions before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing questions."))

        created = 0
        for q_data in QUESTIONS:
            choices_data = q_data.pop("choices", [])
            question = Question.objects.create(**q_data)
            for c in choices_data:
                Choice.objects.create(question=question, **c)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created} questions."))