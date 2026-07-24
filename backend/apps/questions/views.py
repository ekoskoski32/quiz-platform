import random
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer, QuestionListSerializer


class IsQuizAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_admin


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.prefetch_related("choices").all().order_by("-created_at")
    permission_classes = [IsQuizAdmin]

    def get_serializer_class(self):
        if self.request.user.is_admin or self.action in ["create", "update", "partial_update"]:
            return QuestionSerializer
        return QuestionListSerializer

    @action(detail=False, methods=["get"], url_path="categories")
    def categories(self, request):
        """GET /api/questions/categories/ — list categories with question counts."""
        from django.db.models import Count
        data = (
            Question.objects
            .values("category")
            .annotate(count=Count("id"))
            .order_by("category")
        )
        return Response([{"category": d["category"], "count": d["count"]} for d in data])