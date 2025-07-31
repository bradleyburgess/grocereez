from typing import cast

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from faker import Faker
import pytest
from pytest_django.asserts import assertContains

from .forms import CustomUserCreationForm

faker = Faker()
User = get_user_model()


@pytest.mark.django_db
class TestUsersManager:
    def test_create_user(self, signup_user):
        user = signup_user
        u = User.objects.create_user(email=user["email"], password=user["password"])  # type: ignore
        assert u.email == user["email"]
        assert u.is_active
        assert not u.is_staff
        assert not u.is_superuser
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            assert u.username is None
        except AttributeError:
            pass
        with pytest.raises(ValueError):
            User.objects.create_user()  # type: ignore
        with pytest.raises(ValueError):
            User.objects.create_user(email="")  # type: ignore
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="foo")  # type: ignore

    def test_create_superuser(self, signup_user):
        user = signup_user
        admin_user = User.objects.create_superuser(
            email=user["email"], password=user["password"]
        )  # type: ignore
        assert admin_user.email == user["email"]
        assert admin_user.is_active
        assert admin_user.is_staff
        assert admin_user.is_superuser
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            assert admin_user.username is None
        except AttributeError:
            pass
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False
            )  # type: ignore


@pytest.mark.django_db
class TestUserSignUp:
    def test_signup_page_has_form(self, client):
        response = cast(HttpResponse, client.get(reverse("users:signup")))
        assert response.status_code == 200
        assert "form" in response.context
        assert isinstance(response.context["form"], CustomUserCreationForm)

    def test_user_can_sign_up(self, client, signup_user):
        user = signup_user
        response = cast(
            HttpResponse,
            client.post(
                reverse("users:signup"),
                data={
                    "email": user["email"],
                    "password1": user["password"],
                    "password2": user["password"],
                    "display_name": user["display_name"],
                },
                follow=True,
            ),
        )
        u = User.objects.first()
        assert u is not None
        assert u.display_name == user["display_name"]  # type: ignore
        assert u.email == user["email"]  # type: ignore
        assertContains(response, "Logout")

    def test_cannot_signup_duplicate_email(self, client, user):
        response = cast(
            HttpResponse,
            client.post(
                reverse("users:signup"),
                data={
                    "email": user["email"],
                    "password1": user["password"],
                    "password2": user["password"],
                    "display_name": user["display_name"],
                },
                follow=True,
            ),
        )
        assertContains(response, "already exists")


@pytest.mark.django_db
class TestUserLogin:
    def test_user_can_login(self, client, user):
        response = cast(
            HttpResponse,
            client.post(
                reverse("users:login"),
                data={
                    "email": user["email"],
                    "password": user["password"],
                },
                follow=True,
            ),
        )
        assert response.status_code == 200
        assert response.context["user"].email == user["email"]
        last_url, _ = response.redirect_chain[-1]
        assert last_url == reverse("dashboard:index")

    def test_invalid_credentials(self, client, user):
        response = cast(
            HttpResponse,
            client.post(
                reverse("users:login"),
                data={
                    "email": faker.email(),
                    "password": faker.password(),
                },
            ),
        )
        assertContains(response, "Invalid credentials")
