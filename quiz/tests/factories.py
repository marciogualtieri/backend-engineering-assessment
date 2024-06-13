import factory

from quiz import models


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.User

    is_staff = False
    is_superuser = False
    username = "test_user"


class QuizFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Quiz


class QuestionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Question


class Choice(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Choice


class AssignmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Assignment


class AnswerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Answer
