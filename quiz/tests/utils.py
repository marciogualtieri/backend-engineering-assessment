import json
import logging
from typing import List, Union

from deepdiff import DeepDiff
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APITestCase

from quiz import models

from . import factories

logger = logging.getLogger(__name__)


class BaseTestCase(APITestCase):

    maxDiff = None

    def setUp(self):
        self.geography_quizzer = factories.UserFactory(
            username="geography_quizzer", is_quizzer=True
        )
        self.biology_quizzer = factories.UserFactory(
            username="biology_quizzer", is_quizzer=True
        )
        self.math_quizzer = factories.UserFactory(
            username="math_quizzer", is_quizzer=True
        )
        self.bob_quizzee = factories.UserFactory(username="bob_quizzee")
        self.alice_quizzee = factories.UserFactory(username="alice_quizzee")

        # Geography quiz
        self.geography_quiz = factories.QuizFactory(
            description="Geography quiz", user=self.geography_quizzer
        )

        # Single correct answer question
        self.whats_the_capital_of_belgium = factories.QuestionFactory(
            text="What's the capital of Belgium?", user=self.geography_quizzer
        )
        self.brussels = factories.Choice(
            question=self.whats_the_capital_of_belgium,
            text="Brussels",
            is_correct=True,
        )
        self.zurich = factories.Choice(
            question=self.whats_the_capital_of_belgium, text="Zurich"
        )
        self.amsterdam = factories.Choice(
            question=self.whats_the_capital_of_belgium, text="Amsterdam"
        )

        # Multiple correct answers question
        self.which_are_european_countries = factories.QuestionFactory(
            text="Which are european countries?", user=self.geography_quizzer
        )
        self.belgium = factories.Choice(
            question=self.which_are_european_countries,
            text="Belgium",
            is_correct=True,
        )
        self.switzerland = factories.Choice(
            question=self.which_are_european_countries,
            text="Switzerland",
            is_correct=True,
        )
        self.japan = factories.Choice(
            question=self.which_are_european_countries, text="Japan"
        )

        self.whats_the_capital_of_belgium.quizzes.add(self.geography_quiz)
        self.which_are_european_countries.quizzes.add(self.geography_quiz)

        # Biology quiz
        self.biology_quiz = factories.QuizFactory(
            description="Biology quiz", user=self.biology_quizzer
        )

        self.which_is_mammal = factories.QuestionFactory(
            text="Which is mammal?", user=self.biology_quizzer
        )
        self.whale = factories.Choice(
            question=self.which_is_mammal,
            text="Whale",
            is_correct=True,
        )
        self.platypus = factories.Choice(question=self.which_is_mammal, text="Platypus")
        self.crocodile = factories.Choice(
            question=self.which_is_mammal, text="Crocodile"
        )

        self.which_is_mammal.quizzes.add(self.biology_quiz)

        # Math questions
        self.which_numbers_are_prime = factories.QuestionFactory(
            text="Which numbers are prime?", user=self.math_quizzer
        )
        self.number_three = factories.Choice(
            question=self.which_numbers_are_prime,
            text="3",
            is_correct=True,
        )
        self.pi = factories.Choice(
            question=self.which_numbers_are_prime,
            text="Pi",
            is_correct=True,
        )
        self.half = factories.Choice(question=self.which_numbers_are_prime, text="1/2")

        self.which_numbers_are_irrational = factories.QuestionFactory(
            text="Which numbers are prime?", user=self.math_quizzer
        )
        self.golden_ratio = factories.Choice(
            question=self.which_numbers_are_prime,
            text="Golden Ratio",
            is_correct=True,
        )
        self.eulers_number = factories.Choice(
            question=self.which_numbers_are_prime,
            text="Euler's Number",
            is_correct=True,
        )
        self.imaginary_unit = factories.Choice(
            question=self.which_numbers_are_prime, text="Imaginary Unit"
        )

        # Bob's Assignments
        self.bob_geography_assignment = factories.AssignmentFactory(
            user=self.bob_quizzee, quiz=self.geography_quiz
        )
        self.bob_biology_assignment = factories.AssignmentFactory(
            user=self.bob_quizzee, quiz=self.biology_quiz
        )
        self.bob_geography_answer = factories.AnswerFactory(
            assignment=self.bob_geography_assignment, choice=self.brussels
        )
        self.bob_biology_answer = factories.AnswerFactory(
            assignment=self.bob_biology_assignment, choice=self.crocodile
        )

        # Alice's Assignments
        self.alice_geography_assignment = factories.AssignmentFactory(
            user=self.alice_quizzee, quiz=self.geography_quiz
        )
        self.alice_biology_assignment = factories.AssignmentFactory(
            user=self.alice_quizzee, quiz=self.biology_quiz
        )
        self.geography_answer = factories.AnswerFactory(
            assignment=self.alice_geography_assignment, choice=self.zurich
        )
        self.biology_answer = factories.AnswerFactory(
            assignment=self.alice_biology_assignment, choice=self.whale
        )

        # Submitted Assignment
        self.alice_submitted_assignment = factories.AssignmentFactory(
            user=self.alice_quizzee, quiz=self.biology_quiz, submited_at=timezone.now()
        )

    def _get(
        self,
        resource: str,
        kwargs: Union[dict, None] = None,
        parameters: Union[dict, None] = None,
        user: Union[models.User, None] = None,
    ) -> Response:
        if parameters is None:
            parameters = {}
        url = reverse(resource, kwargs=kwargs) if kwargs else reverse(resource)
        if user:
            self.client.force_login(user=user)
        response = self.client.get(url, parameters, format="json")
        self._log_response(response)
        return response

    def _post(
        self,
        resource: str,
        payload: Union[List[dict], dict, None] = None,
        kwargs: Union[dict, None] = None,
        user: Union[models.User, None] = None,
    ) -> Response:
        if user:
            self.client.force_login(user=user)
        url = reverse(resource, kwargs=kwargs) if kwargs else reverse(resource)
        response = self.client.post(url, payload, format="json")
        self._log_response(response)
        return response

    def _get_content(self, response: Response) -> Union[List[dict], dict]:
        return json.loads(response.content.decode("utf-8"))

    @staticmethod
    def _log_response(response: Response) -> None:
        logger.debug(
            "RESPONSE TO %s: %s",
            json.dumps(response.request, indent=4, default=str),
            (
                json.dumps(response.json(), indent=4)
                if response["content-type"] == "application/json"
                else response.content
            ),
        )

    def _assert_response(
        self,
        response: Response,
        status: int,
        expected_payload: Union[List[dict], dict],
        exclude_regex_paths: Union[List[str], None] = None,
    ) -> None:
        self.assertEqual(response.status_code, status)

        actual_payload = self._get_content(response)

        diff = DeepDiff(
            expected_payload,
            actual_payload,
            ignore_order=True,
            exclude_regex_paths=exclude_regex_paths,
        )
        if diff:
            raise AssertionError(f"Input data differ: {diff}")
