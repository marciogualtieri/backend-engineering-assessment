import logging

from rest_framework import serializers

from . import models

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ["id", "username"]


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Choice
        fields = ["id", "text", "is_correct"]


# List serializers


class QuestionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Question
        fields = ["id", "text", "quizzes"]


class QuizListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Quiz
        fields = ["id", "description"]


class AssignmentListQuizzeeSerializer(serializers.ModelSerializer):

    quiz = QuizListSerializer()
    progress = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = models.Assignment
        fields = ["id", "submited_at", "quiz", "progress", "score"]

    def get_progress(self, instance):
        return instance.progress

    def get_score(self, instance):
        return instance.score


class AssignmentListQuizzerSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    quiz = QuizListSerializer()
    progress = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = models.Assignment
        fields = ["id", "user", "submited_at", "quiz", "progress", "score"]

    def get_progress(self, instance):
        return instance.progress

    def get_score(self, instance):
        return instance.score


class AnswerListSerializer(serializers.ModelSerializer):

    question = serializers.SerializerMethodField()

    class Meta:
        model = models.Answer
        fields = ["id", "assignment", "question", "choice"]

    def get_question(self, instance):
        return instance.choice.question.id


# Detail serializers


class ChoiceQuizzeeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Choice
        fields = ["id", "text"]


class QuestionQuizzerDetailSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(many=True)
    quizzes = QuizListSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ["id", "text", "choices", "quizzes"]


class QuestionQuizzeeDetailSerializer(serializers.ModelSerializer):

    choices = ChoiceQuizzeeDetailSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ["id", "text", "choices"]


class QuizQuizzerDetailSerializer(serializers.ModelSerializer):

    questions = QuestionQuizzerDetailSerializer(many=True)

    class Meta:
        model = models.Quiz
        fields = ["id", "description", "questions"]


class QuizQuizzeeDetailSerializer(serializers.ModelSerializer):

    questions = QuestionQuizzeeDetailSerializer(many=True)

    class Meta:
        model = models.Quiz
        fields = ["id", "description", "questions"]


class AssignmentQuizzerDetailSerializer(serializers.ModelSerializer):

    quiz = QuizQuizzerDetailSerializer()
    user = UserSerializer()

    class Meta:
        model = models.Assignment
        fields = ["id", "user", "submited_at", "quiz"]


class AssignmentQuizzeeDetailSerializer(serializers.ModelSerializer):

    quiz = QuizQuizzeeDetailSerializer()

    class Meta:
        model = models.Assignment
        fields = ["id", "submited_at", "quiz"]


class AnswerDetailSerializer(serializers.ModelSerializer):

    question = serializers.SerializerMethodField()
    choice = ChoiceQuizzeeDetailSerializer()

    class Meta:
        model = models.Answer
        fields = ["id", "assignment", "question", "choice"]

    def get_question(self, instance):
        return QuestionQuizzeeDetailSerializer(instance.choice.question).data


# Create serializers


class QuestionCreateSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ["id", "text", "choices"]

    def create(self, validated_data):
        user = self.context["request"].user
        question = models.Question.objects.create(
            text=validated_data["text"], user=user
        )
        models.Choice.objects.bulk_create(
            [
                models.Choice(question=question, **choice)
                for choice in validated_data["choices"]
            ]
        )
        return question


class QuizCreateSerializer(serializers.ModelSerializer):

    questions = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = models.Quiz
        fields = ["id", "description", "questions"]

    def create(self, validated_data):
        questions = models.Question.objects.filter(pk__in=validated_data["questions"])
        user = self.context["request"].user
        quiz = models.Quiz.objects.create(
            description=validated_data["description"], user=user
        )
        quiz.questions.add(*questions)
        return quiz

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "description": instance.description,
            "questions": instance.questions.values_list("id", flat=True),
        }


class AssignmentCreateSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField()
    quiz = serializers.IntegerField()

    class Meta:
        model = models.Assignment
        fields = ["id", "user", "quiz"]

    def create(self, validated_data):
        user = models.User.objects.get(pk=validated_data["user"])
        quiz = models.Quiz.objects.get(pk=validated_data["quiz"])
        assignment = models.Assignment.objects.create(user=user, quiz=quiz)
        return assignment

    def to_representation(self, instance):
        return {"id": instance.id, "user": instance.user.id, "quiz": instance.quiz.id}


class AnswerCreateSerializer(serializers.ModelSerializer):

    assignment = serializers.IntegerField()
    choice = serializers.IntegerField()

    class Meta:
        model = models.Answer
        fields = ["id", "assignment", "choice"]

    def create(self, validated_data):
        assignment = models.Assignment.objects.get(pk=validated_data["assignment"])
        choice = models.Choice.objects.get(pk=validated_data["choice"])
        answer = models.Answer.objects.create(assignment=assignment, choice=choice)
        return answer

    def validate_assignment(self, value):
        assignment = models.Assignment.objects.get(pk=value)
        if assignment and assignment.submited_at is not None:
            raise serializers.ValidationError(
                "The assigment has already been submitted."
            )
        return value

    def validate_choice(self, value):
        assignment = models.Assignment.objects.get(pk=self.initial_data["assignment"])
        choice = models.Choice.objects.get(pk=value)
        if not assignment.quiz.questions.contains(choice.question):
            raise serializers.ValidationError(
                "The choice is not an valid answer to the assignment's quiz."
            )
        return value

    def to_representation(self, instance):
        return {"assignment": instance.assignment.id, "choice": instance.choice.id}
