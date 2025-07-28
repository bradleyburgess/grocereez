from typing import cast
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from .models import Household

faker = Faker()
User = get_user_model()

display_name = faker.name_nonbinary()
email = faker.email()
password = faker.password()
household_name = faker.last_name() + " Household"

print(email)


class HouseholdModelTest(TestCase):
    faker = Faker()

    def test_create_household(self):
        u_name = self.faker.name_nonbinary()
        u_email = self.faker.email()
        u_password = self.faker.password()
        h_name = self.faker.last_name() + " Household"
        u = User.objects.create_user(
            email=u_email, password=u_password, display_name=u_name
        )  # type: ignore
        h = Household.objects.create(name=h_name, created_by=u)
        result = cast(Household, Household.objects.first())
        self.assertIsNotNone(result)
        self.assertEqual(h, result)
        self.assertEqual(h_name, result.name)
        self.assertEqual(result.created_by, u)
        self.assertIsInstance(result.uuid, uuid.UUID)


class HouseholdListTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        User.objects.create_user(
            email=email, password=password, display_name=display_name
        )  # type: ignore

    def test_unauthenticated_redirected_to_login(self):
        response = self.client.get(reverse("households:index"))
        self.assertEqual(302, response.status_code)
        response = self.client.get(reverse("households:index"), follow=True)
        self.assertIn("login", response.redirect_chain[-1][0])

    def test_authenticated_gets_page(self):
        logged_in = self.client.login(email=email, password=password)
        self.assertTrue(logged_in)
        response = self.client.get(reverse("households:index"))
        self.assertContains(response, "My Households")

    def test_no_households_prompt_to_create(self):
        logged_in = self.client.login(email=email, password=password)
        self.assertTrue(logged_in)
        response = (
            self.client.get(reverse("households:index")).content.decode("utf-8").lower()
        )
        self.assertIn("create a household", response)

    # def test_user_has_household_lists_household(self):
    #     user = User.objects.get(email=email)
    #     household = Household.objects.create(name=household_name, created_by=user)
    #     logged_in = self.client.login(email=email, password=password)
    #     self.assertTrue(logged_in)
    #     response = (
    #         self.client.get(reverse("households:index")).content.decode("utf-8").lower()
    #     )
    #     self.assertIn("create a household", response)
