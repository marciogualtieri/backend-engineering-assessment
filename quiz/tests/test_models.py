from . import factories
from .utils import BaseTestCase


class ModelsTest(BaseTestCase):

    def test_answered_only_single_correct_answer_question(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.brussels)

        self.assertEqual(assignment.score, 50.0)
        self.assertEqual(assignment.progress, 50.0)

    def test_answered_only_multiple_correct_answers_question(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.zurich)

        self.assertEqual(assignment.score, 0.0)
        self.assertEqual(assignment.progress, 50.0)

    def test_scored_only_single_correct_answer_question(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.brussels)
        factories.AnswerFactory(assignment=assignment, choice=self.japan)

        self.assertEqual(assignment.score, 50.0)
        self.assertEqual(assignment.progress, 100.0)

    def test_scored_only_multiple_correct_answers_question(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.belgium)
        factories.AnswerFactory(assignment=assignment, choice=self.switzerland)

        self.assertEqual(assignment.score, 50.0)
        self.assertEqual(assignment.progress, 50.0)

    def test_scored_all_questions(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.brussels)
        factories.AnswerFactory(assignment=assignment, choice=self.belgium)
        factories.AnswerFactory(assignment=assignment, choice=self.switzerland)

        self.assertEqual(assignment.score, 100.0)
        self.assertEqual(assignment.progress, 100.0)

    def test_missed_all_questions(self):

        assignment = factories.AssignmentFactory(
            user=self.geography_quizzer, quiz=self.geography_quiz
        )

        factories.AnswerFactory(assignment=assignment, choice=self.zurich)
        factories.AnswerFactory(assignment=assignment, choice=self.japan)

        self.assertEqual(assignment.score, 0.0)
        self.assertEqual(assignment.progress, 100.0)
