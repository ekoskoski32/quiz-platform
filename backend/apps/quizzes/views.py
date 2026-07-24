import json
import random
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.questions.models import Question, Choice
from .grading import grade_answer
from .models import Answer, Attempt
from .serializers import AttemptListSerializer, AttemptSerializer

QUIZ_SIZE = 5


class AttemptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return AttemptListSerializer
        return AttemptSerializer

    def create(self, request):
        """POST /api/attempts/ — start a quiz. Optional body: {category: str}"""
        category = request.data.get("category")
        qs = Question.objects.all()
        if category and category != "random":
            qs = qs.filter(category=category)

        all_questions = list(qs)
        if len(all_questions) < QUIZ_SIZE:
            return Response(
                {"error": f"Not enough questions. Need at least {QUIZ_SIZE}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        selected = random.sample(all_questions, QUIZ_SIZE)
        attempt = Attempt.objects.create(user=request.user)
        attempt.questions.set(selected)
        return Response(
            AttemptSerializer(attempt, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        attempt = self.get_object()
        if attempt.submitted_at:
            return Response({"error": "Attempt already submitted."}, status=400)

        raw_answers = request.data.get("answers", "[]")
        if isinstance(raw_answers, str):
            try:
                answers_data = json.loads(raw_answers)
            except json.JSONDecodeError:
                return Response({"error": "Invalid answers JSON."}, status=400)
        else:
            answers_data = raw_answers

        question_ids = list(attempt.questions.values_list("id", flat=True))
        correct_count = 0

        for ans_data in answers_data:
            q_id = ans_data.get("question_id")
            if q_id not in question_ids:
                continue
            question = Question.objects.get(pk=q_id)
            answer, _ = Answer.objects.get_or_create(attempt=attempt, question=question)
            answer.text_response = ans_data.get("text_response", "")
            image_file = request.FILES.get(f"image_{q_id}")
            if image_file:
                answer.image_response = image_file
            choice_ids = ans_data.get("selected_choice_ids", [])
            if choice_ids:
                answer.selected_choices.set(
                    Choice.objects.filter(id__in=choice_ids, question=question)
                )
            answer.save()
            result = grade_answer(answer)
            answer.is_correct = result["is_correct"]
            answer.ai_feedback = result["ai_feedback"]
            answer.graded_at = timezone.now()
            answer.save()
            if result["is_correct"] is True:
                correct_count += 1

        attempt.score = float(correct_count)
        attempt.submitted_at = timezone.now()
        attempt.save()
        return Response(AttemptSerializer(attempt, context={"request": request}).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """GET /api/attempts/stats/ — overall + per-category stats for the user."""
        from django.db.models import Count, Sum, Q
        from apps.quizzes.models import Answer

        submitted = Attempt.objects.filter(
            user=request.user,
            submitted_at__isnull=False,
        )
        total_attempts = submitted.count()
        if total_attempts == 0:
            return Response({
                "total_attempts": 0,
                "overall_pct": 0,
                "by_category": [],
            })

        total_score = sum(a.score for a in submitted if a.score is not None)
        overall_pct = round((total_score / (total_attempts * QUIZ_SIZE)) * 100)

        # Per-category: look at individual answers
        answers = Answer.objects.filter(
            attempt__user=request.user,
            attempt__submitted_at__isnull=False,
            is_correct__isnull=False,
        ).select_related("question")

        cat_stats = {}
        for ans in answers:
            cat = ans.question.category
            if cat not in cat_stats:
                cat_stats[cat] = {"correct": 0, "total": 0}
            cat_stats[cat]["total"] += 1
            if ans.is_correct:
                cat_stats[cat]["correct"] += 1

        by_category = sorted([
            {
                "category": cat,
                "correct": v["correct"],
                "total": v["total"],
                "pct": round((v["correct"] / v["total"]) * 100),
            }
            for cat, v in cat_stats.items()
        ], key=lambda x: -x["pct"])

        return Response({
            "total_attempts": total_attempts,
            "overall_pct": overall_pct,
            "by_category": by_category,
        })