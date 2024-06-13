from freezegun import freeze_time
from rest_framework import status

from .utils import BaseTestCase


class QuestionViewSetTests(BaseTestCase):

    def test_get_specific_user_questions(self):
        response = self._get_questions(user=self.geography_quizzer)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.whats_the_capital_of_belgium.id,
                    "text": "What's the capital of Belgium?",
                    "quizzes": [self.geography_quiz.id],
                },
                {
                    "id": self.which_are_european_countries.id,
                    "text": "Which are european countries?",
                    "quizzes": [self.geography_quiz.id],
                },
            ],
        )

    def test_get_question(self):
        response = self._get_question(
            self.which_is_mammal.id, user=self.biology_quizzer
        )
        self._assert_response(
            response,
            status.HTTP_200_OK,
            {
                "id": self.which_is_mammal.id,
                "text": "Which is mammal?",
                "choices": [
                    {"id": self.whale.id, "text": "Whale", "is_correct": True},
                    {"id": self.platypus.id, "text": "Platypus", "is_correct": False},
                    {"id": self.crocodile.id, "text": "Crocodile", "is_correct": False},
                ],
                "quizzes": [{"id": 2, "description": "Biology quiz"}],
            },
        )

    def test_create_question(self):
        response = self._create_question(
            {
                "text": "Which are birds?",
                "choices": [
                    {"text": "Bald Eagle", "is_correct": True},
                    {"text": "Canary", "is_correct": True},
                    {"text": "Platypus", "is_correct": False},
                ],
            },
            user=self.biology_quizzer,
        )
        self._assert_response(
            response,
            status.HTTP_201_CREATED,
            {
                "text": "Which are birds?",
                "choices": [
                    {"text": "Bald Eagle", "is_correct": True},
                    {"text": "Canary", "is_correct": True},
                    {"text": "Platypus", "is_correct": False},
                ],
            },
            exclude_regex_paths=[r"root\['id'\]", r"root\['choices'\]\[\d+\]\['id'\]"],
        )

    def test_quizzee_attempt_create_question(self):
        response = self._create_question(
            {},
            user=self.bob_quizzee,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _get_questions(self, parameters=None, user=None):
        return self._get("questions-list", parameters=parameters, user=user)

    def _get_question(self, question_id, parameters=None, user=None):
        return self._get(
            "questions-detail",
            kwargs={"pk": question_id},
            parameters=parameters,
            user=user,
        )

    def _create_question(self, question, user=None):
        return self._post("questions-list", question, user=user)


class QuizViewSetTests(BaseTestCase):

    def test_get_specific_user_quizzes(self):
        response = self._get_quizzes(user=self.geography_quizzer)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.geography_quiz.id,
                    "description": "Geography quiz",
                }
            ],
        )

    def test_get_specifc_quiz(self):
        response = self._get_quiz(self.biology_quiz.id, user=self.biology_quizzer)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            {
                "id": self.biology_quiz.id,
                "description": "Biology quiz",
                "questions": [
                    {
                        "id": self.which_is_mammal.id,
                        "text": "Which is mammal?",
                        "choices": [
                            {"id": self.whale.id, "text": "Whale", "is_correct": True},
                            {
                                "id": self.platypus.id,
                                "text": "Platypus",
                                "is_correct": False,
                            },
                            {
                                "id": self.crocodile.id,
                                "text": "Crocodile",
                                "is_correct": False,
                            },
                        ],
                        "quizzes": [
                            {"id": self.biology_quiz.id, "description": "Biology quiz"}
                        ],
                    }
                ],
            },
        )

    def test_create_quiz(self):
        response = self._create_quiz(
            {
                "description": "Math Quiz",
                "questions": [
                    self.which_numbers_are_prime.id,
                    self.which_numbers_are_irrational.id,
                ],
            },
            user=self.math_quizzer,
        )
        self._assert_response(
            response,
            status.HTTP_201_CREATED,
            {"description": "Math Quiz", "questions": [4, 5]},
            exclude_regex_paths=[r"root\['id'\]"],
        )

    def test_quizzee_attempt_create_quiz(self):
        response = self._create_quiz(
            {},
            user=self.bob_quizzee,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_quizzee_quizzes(self):
        response = self._get_quizzes(user=self.bob_quizzee)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {"id": self.geography_quiz.id, "description": "Geography quiz"},
                {"id": self.biology_quiz.id, "description": "Biology quiz"},
            ],
        )

    def _get_quizzes(self, parameters=None, user=None):
        return self._get("quizzes-list", parameters=parameters, user=user)

    def _get_quiz(self, quizz_id, parameters=None, user=None):
        return self._get(
            "quizzes-detail",
            kwargs={"pk": quizz_id},
            parameters=parameters,
            user=user,
        )

    def _create_quiz(self, question, user=None):
        return self._post("quizzes-list", question, user=user)


class AssignmentViewSetTests(BaseTestCase):

    def test_get_quizzee_assignments(self):
        response = self._get_assignments(user=self.bob_quizzee)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.bob_geography_assignment.id,
                    "submited_at": None,
                    "quiz": {
                        "id": self.geography_quiz.id,
                        "description": "Geography quiz",
                    },
                    "progress": 50.0,
                    "score": 50.0,
                },
                {
                    "id": self.bob_biology_assignment.id,
                    "submited_at": None,
                    "quiz": {"id": self.biology_quiz.id, "description": "Biology quiz"},
                    "progress": 100.0,
                    "score": 0.0,
                },
            ],
        )

    def test_get_quizzee_assignments_filtered_by_quiz(self):
        response = self._get_assignments(
            user=self.bob_quizzee, parameters={"quiz_id": self.geography_quiz.id}
        )
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.bob_geography_assignment.id,
                    "submited_at": None,
                    "quiz": {
                        "id": self.geography_quiz.id,
                        "description": "Geography quiz",
                    },
                    "progress": 50.0,
                    "score": 50.0,
                }
            ],
        )

    def test_get_quizzer_assignments(self):
        response = self._get_assignments(user=self.geography_quizzer)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.bob_geography_assignment.id,
                    "user": {"id": self.bob_quizzee.id, "username": "bob_quizzee"},
                    "submited_at": None,
                    "quiz": {
                        "id": self.geography_quiz.id,
                        "description": "Geography quiz",
                    },
                    "progress": 50.0,
                    "score": 50.0,
                },
                {
                    "id": self.alice_geography_assignment.id,
                    "user": {"id": self.alice_quizzee.id, "username": "alice_quizzee"},
                    "submited_at": None,
                    "quiz": {
                        "id": self.geography_quiz.id,
                        "description": "Geography quiz",
                    },
                    "progress": 50.0,
                    "score": 0.0,
                },
            ],
        )

    def test_get_quizzer_assignments_filtered_by_user(self):
        response = self._get_assignments(
            user=self.geography_quizzer, parameters={"user_id": self.bob_quizzee.id}
        )
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.bob_geography_assignment.id,
                    "user": {"id": self.bob_quizzee.id, "username": "bob_quizzee"},
                    "submited_at": None,
                    "quiz": {
                        "id": self.geography_quiz.id,
                        "description": "Geography quiz",
                    },
                    "progress": 50.0,
                    "score": 50.0,
                }
            ],
        )

    def test_get_assignment(self):
        response = self._get_assignment(
            self.bob_geography_assignment.id, user=self.bob_quizzee
        )
        self._assert_response(
            response,
            status.HTTP_200_OK,
            {
                "id": self.bob_geography_assignment.id,
                "submited_at": None,
                "quiz": {
                    "id": self.geography_quiz.id,
                    "description": "Geography quiz",
                    "questions": [
                        {
                            "id": self.whats_the_capital_of_belgium.id,
                            "text": "What's the capital of Belgium?",
                            "choices": [
                                {"id": self.brussels.id, "text": "Brussels"},
                                {"id": self.zurich.id, "text": "Zurich"},
                                {"id": self.amsterdam.id, "text": "Amsterdam"},
                            ],
                        },
                        {
                            "id": self.which_are_european_countries.id,
                            "text": "Which are european countries?",
                            "choices": [
                                {"id": self.belgium.id, "text": "Belgium"},
                                {"id": self.switzerland.id, "text": "Switzerland"},
                                {"id": self.japan.id, "text": "Japan"},
                            ],
                        },
                    ],
                },
            },
        )

    def test_create_assigment(self):
        response = self._create_assignment(
            {
                "user": self.bob_quizzee.id,
                "quiz": self.biology_quiz.id,
            },
            user=self.biology_quizzer,
        )
        self._assert_response(
            response,
            status.HTTP_201_CREATED,
            {"user": self.bob_quizzee.id, "quiz": self.biology_quiz.id},
            exclude_regex_paths=[r"root\['id'\]"],
        )

    def test_quizzee_attempt_create_assigment(self):
        response = self._create_assignment(
            {},
            user=self.bob_quizzee,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time("2024-06-12")
    def test_submit_assignment(self):
        response = self._submit_assignment(
            self.bob_geography_assignment.id, user=self.bob_quizzee
        )
        self._assert_response(
            response,
            status.HTTP_200_OK,
            {
                "id": self.bob_geography_assignment.id,
                "submited_at": "2024-06-12T00:00:00Z",
                "quiz": {
                    "id": self.geography_quiz.id,
                    "description": "Geography quiz",
                    "questions": [
                        {
                            "id": self.whats_the_capital_of_belgium.id,
                            "text": "What's the capital of Belgium?",
                            "choices": [
                                {"id": self.brussels.id, "text": "Brussels"},
                                {"id": self.zurich.id, "text": "Zurich"},
                                {"id": self.amsterdam.id, "text": "Amsterdam"},
                            ],
                        },
                        {
                            "id": self.which_are_european_countries.id,
                            "text": "Which are european countries?",
                            "choices": [
                                {"id": self.belgium.id, "text": "Belgium"},
                                {"id": self.switzerland.id, "text": "Switzerland"},
                                {"id": self.japan.id, "text": "Japan"},
                            ],
                        },
                    ],
                },
            },
        )

    def test_quizzer_attempt_submit_assignment(self):
        response = self._submit_assignment(
            self.bob_geography_assignment.id, user=self.biology_quizzer
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _get_assignments(self, parameters=None, user=None):
        return self._get("assignments-list", parameters=parameters, user=user)

    def _get_assignment(self, assignment_id, parameters=None, user=None):
        return self._get(
            "assignments-detail",
            kwargs={"pk": assignment_id},
            parameters=parameters,
            user=user,
        )

    def _submit_assignment(self, assignment_id, user=None):
        return self._post(
            "assignments-submit",
            kwargs={"pk": assignment_id},
            user=user,
        )

    def _create_assignment(self, assignment, user=None):
        return self._post("assignments-list", assignment, user=user)


class AnswerViewSetTests(BaseTestCase):

    def test_get_answers(self):
        response = self._get_answers(user=self.bob_quizzee)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            [
                {
                    "id": self.bob_geography_answer.id,
                    "assignment": self.bob_geography_assignment.id,
                    "choice": self.brussels.id,
                    "question": self.whats_the_capital_of_belgium.id,
                },
                {
                    "id": self.bob_biology_answer.id,
                    "assignment": self.bob_biology_assignment.id,
                    "question": self.which_is_mammal.id,
                    "choice": self.crocodile.id,
                },
            ],
        )

    def test_get_answer(self):
        response = self._get_answer(self.bob_geography_answer.id, user=self.bob_quizzee)
        self._assert_response(
            response,
            status.HTTP_200_OK,
            {
                "id": self.bob_geography_answer.id,
                "assignment": self.bob_geography_assignment.id,
                "question": {
                    "id": self.whats_the_capital_of_belgium.id,
                    "text": "What's the capital of Belgium?",
                    "choices": [
                        {"id": self.brussels.id, "text": "Brussels"},
                        {"id": self.zurich.id, "text": "Zurich"},
                        {"id": self.amsterdam.id, "text": "Amsterdam"},
                    ],
                },
                "choice": {"id": self.brussels.id, "text": "Brussels"},
            },
        )

    def test_create_answer(self):
        response = self._create_answer(
            {
                "assignment": self.bob_geography_assignment.id,
                "choice": self.amsterdam.id,
            },
            user=self.bob_quizzee,
        )
        self._assert_response(
            response,
            status.HTTP_201_CREATED,
            {
                "assignment": self.bob_geography_assignment.id,
                "choice": self.amsterdam.id,
            },
            exclude_regex_paths=[r"root\['id'\]"],
        )

    def test_attempt_create_answer_with_invalid_choice(self):
        response = self._create_answer(
            {"assignment": self.bob_geography_assignment.id, "choice": self.whale.id},
            user=self.bob_quizzee,
        )
        self._assert_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            {"choice": ["The choice is not an valid answer to the assignment's quiz."]},
        )

    def test_attempt_create_answer_for_submitted_assignment(self):
        response = self._create_answer(
            {"assignment": self.alice_submitted_assignment.id, "choice": self.whale.id},
            user=self.alice_quizzee,
        )
        self._assert_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            {"assignment": ["The assigment has already been submitted."]},
        )

    def test_quizzer_attempt_create_answer(self):
        response = self._create_answer(
            {},
            user=self.biology_quizzer,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _get_answers(self, parameters=None, user=None):
        return self._get("answers-list", parameters=parameters, user=user)

    def _get_answer(self, answer_id, parameters=None, user=None):
        return self._get(
            "answers-detail",
            kwargs={"pk": answer_id},
            parameters=parameters,
            user=user,
        )

    def _create_answer(self, answer, user=None):
        return self._post("answers-list", answer, user=user)
