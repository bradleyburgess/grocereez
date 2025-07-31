from typing import cast

from django.test import Client
from django.http import HttpResponse
from django.urls import reverse
import pytest
from pytest_django.asserts import assertContains, assertNotContains


@pytest.mark.django_db
class TestDashboard:
    def test_signup_and_login_are_on_page(self, client: Client):
        response = cast(HttpResponse, client.get(reverse("home")))
        assert response.status_code == 200
        assertContains(response, "signup")
        assertContains(response, "login")

    def test_signout_on_page(self, client: Client, user):
        logged_in = client.login(email=user["email"], password=user["password"])
        assert logged_in
        response = cast(HttpResponse, client.get(reverse("home"), follow=True))
        assert response.status_code == 200
        assertNotContains(response, "signup")
        assert "logout" in response.content.decode("utf-8").lower()

    def test_unauthenticated_redirected_to_login(self, client: Client):
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        assert response.status_code == 302
        response = cast(
            HttpResponse, client.get(reverse("dashboard:index"), follow=True)
        )
        assert "login" in response.redirect_chain[-1][0]
