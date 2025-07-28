from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_signup_and_login_are_on_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "signup")
        self.assertContains(response, "login")

    def test_signout_on_page(self):
        User = get_user_model()
        User.objects.create_user(email="normal@user.com", password="testing1234")  # type: ignore
        logged_in = self.client.login(email="normal@user.com", password="testing1234")
        self.assertTrue(logged_in)
        response = self.client.get(reverse("home"), follow=True)
        self.assertNotContains(response, "signup")
        self.assertIn(
            "logout",
            response.content.decode("utf-8").lower(),
        )

    def test_unauthenticated_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(302, response.status_code)
        response = self.client.get(reverse("dashboard:index"), follow=True)
        self.assertIn("login", response.redirect_chain[-1][0])
