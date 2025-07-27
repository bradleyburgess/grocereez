from faker import Faker
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import CustomUserCreationForm


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")  # type: ignore
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_user()  # type: ignore
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")  # type: ignore
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")  # type: ignore

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email="super@user.com", password="foo"
        )  # type: ignore
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False
            )  # type: ignore


class UserSignUpTest(TestCase):
    faker = Faker()

    def test_signup_page_has_form(self):
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_user_can_sign_up(self):
        email = self.faker.email()
        password = self.faker.password()
        display_name = self.faker.name_nonbinary()

        response = self.client.post(
            reverse("users:signup"),
            data={
                "email": email,
                "password1": password,
                "password2": password,
                "display_name": display_name,
            },
            follow=True,
        )
        User = get_user_model()
        user = User.objects.first()
        self.assertIsNotNone(user)
        self.assertEqual(user.display_name, display_name)  # type: ignore
        self.assertEqual(user.email, email)  # type: ignore
        self.assertContains(response, "Logout")

    def test_cannot_signup_duplicate_email(self):
        email = self.faker.email()
        password = self.faker.password()
        User = get_user_model()
        User.objects.create_user(
            email=email, password=password, display_name=self.faker.name_nonbinary()
        )  # type: ignore
        response = self.client.post(
            reverse("users:signup"),
            data={
                "email": email,
                "password1": password,
                "password2": password,
                "display_name": self.faker.name_nonbinary(),
            },
            follow=True,
        )
        self.assertContains(response, "already exists")


class UserLoginTest(TestCase):
    faker = Faker()

    def test_user_can_login(self):
        email = self.faker.email()
        password = self.faker.password()
        display_name = self.faker.name_nonbinary()
        last_name = self.faker.last_name()
        User = get_user_model()
        user = User.objects.create_user(
            email=email,
            password=password,
            display_name=display_name,
            first_name=display_name,
            last_name=last_name,
        )  # type: ignore
        response = self.client.post(
            reverse("users:login"),
            data={
                "email": email,
                "password": password,
            },
            follow=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["user"].email, user.email)
        last_url, _ = response.redirect_chain[-1]
        self.assertEqual(last_url, reverse("dashboard:index"))

    def test_invalid_credentials(self):
        email = self.faker.email()
        password = self.faker.password()
        response = self.client.post(
            reverse("users:login"),
            data={
                "email": email,
                "password": password,
            },
        )
        self.assertContains(response, "Invalid credentials")
