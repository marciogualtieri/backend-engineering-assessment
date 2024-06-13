import django.contrib.auth.models as auth_models
from django.db import models
from django.utils import timezone


class User(auth_models.AbstractUser):
    is_quizzer = models.BooleanField(default=False)


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class Question(BaseModel):

    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"text='{self.text}' | user={self.user.username}"


class Quiz(BaseModel):

    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name="quizzes")

    class Meta:
        verbose_name_plural = "quizzes"

    def __str__(self):
        return f"description='{self.description}' | user={self.user.username}"


class Choice(BaseModel):

    text = models.TextField()
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"question={self.question} | text='{self.text}' | is_correct={self.is_correct}"


class Assignment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="assignments")
    submited_at = models.DateTimeField(null=True, blank=True)

    @property
    def score(self):
        """
        Quiz score calculated as "all or nothing", that is, the selected choices need to match the correct choices
        perfectly.
        """
        total = 0

        for question in self.quiz.questions.all():
            correct_choices = [
                choice.id
                for choice in question.choices.order_by("id").all()
                if choice.is_correct
            ]
            selected_choices = [
                answer.choice.id
                for answer in self.answers.filter(choice__question=question)
                .order_by("choice_id")
                .all()
            ]
            total += 1.0 if selected_choices == correct_choices else 0.0

        return total / self.quiz.questions.count() * 100

    @property
    def progress(self):
        """
        Quiz progress calculated as the percentage of answered questions.
        """
        total = self.quiz.questions.count()
        count = self.answers.values("choice__question").distinct().count()

        return count / total * 100

    def __str__(self):
        return f"{self.quiz.description} | {self.user} | {self.submited_at if self.submited_at else 'PENDING'}"


class Answer(models.Model):

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="answers"
    )
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    unique_together = [["user", "assignment", "choice"]]

    def __str__(self):
        return f"question={self.choice} | user={self.assignment.user.username}"
