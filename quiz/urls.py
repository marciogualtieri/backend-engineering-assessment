from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"questions", views.QuestionViewSet, basename="questions")
router.register(r"assignments", views.AssignmentViewSet, basename="assignments")
router.register(r"answers", views.AnswerViewSet, basename="answers")
router.register(r"", views.QuizViewSet, basename="quizzes")

urlpatterns = [path("", include(router.urls))]
