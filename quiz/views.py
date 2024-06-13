from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import permissions as drf_permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, permissions, serializers


class BaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    TODO: Add implementations for update and delete.
    """

    pass


class QuestionViewSet(BaseViewSet):

    permission_classes = [
        drf_permissions.IsAuthenticated,
        permissions.IsQuizzer | permissions.IsQuizzeeReader,  # type: ignore
    ]

    def get_queryset(self):
        user = self.request.user
        return models.Question.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.QuestionCreateSerializer
        if self.action == "list":
            return serializers.QuestionListSerializer
        return serializers.QuestionQuizzerDetailSerializer


class QuizViewSet(BaseViewSet):

    permission_classes = [
        drf_permissions.IsAuthenticated,
        permissions.IsQuizzer | permissions.IsQuizzeeReader,  # type: ignore
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_quizzer:
            return models.Quiz.objects.filter(user=user)
        return models.Quiz.objects.filter(assignments__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.QuizCreateSerializer
        if self.action == "list":
            return serializers.QuizListSerializer
        if self.request.user.is_quizzer:
            return serializers.QuizQuizzerDetailSerializer
        return serializers.QuizQuizzeeDetailSerializer


class AssignmentViewSet(BaseViewSet):
    # pylint: disable=unused-argument

    permission_classes = [
        drf_permissions.IsAuthenticated,
        permissions.IsQuizzerNotSubmiter  # type: ignore
        | permissions.IsQuizzeeReader  # type: ignore
        | permissions.IsQuizzeeSubmiter,  # type: ignore
    ]

    def get_queryset(self):
        user = self.request.user
        assignments = (
            models.Assignment.objects.filter(quiz__user=user)
            if user.is_quizzer
            else models.Assignment.objects.filter(user=user)
        )
        return self._filter_by_query_params(assignments)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AssignmentCreateSerializer
        if self.action == "list":
            if self.request.user.is_quizzer:
                return serializers.AssignmentListQuizzerSerializer
            return serializers.AssignmentListQuizzeeSerializer

        if self.request.user.is_quizzer:
            return serializers.AssignmentQuizzerDetailSerializer
        return serializers.AssignmentQuizzeeDetailSerializer

    def _filter_by_query_params(self, assignments):
        filters = {
            key: self.request.query_params[key]
            for key in ["quiz_id", "user_id"]
            if key in self.request.query_params
        }
        return assignments.filter(**filters)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="Filter by User's ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "quiz_id",
                openapi.IN_QUERY,
                description="Filter by Quiz's ID ",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        assignment = self.get_object()
        assignment.submited_at = timezone.now()
        assignment.save(update_fields=["submited_at"])
        return Response(serializers.AssignmentQuizzeeDetailSerializer(assignment).data)


class AnswerViewSet(BaseViewSet):

    permission_classes = [
        drf_permissions.IsAuthenticated,
        permissions.IsQuizzee | permissions.IsQuizzerReader,  # type: ignore
    ]

    def get_queryset(self):
        user = self.request.user
        return models.Answer.objects.filter(assignment__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AnswerCreateSerializer
        if self.action == "list":
            return serializers.AnswerListSerializer
        return serializers.AnswerDetailSerializer
