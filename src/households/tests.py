from typing import cast
import uuid

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from faker import Faker
import pytest
from pytest_django.asserts import assertRedirects, assertContains

from .forms import HouseholdCreateForm
from .models import Household, HouseholdMember

faker = Faker()
User = get_user_model()


@pytest.fixture
def user(db):
    email = faker.email()
    password = faker.password()
    display_name = faker.name_nonbinary()
    last_name = faker.last_name()
    return {
        "user": User.objects.create_user(
            email=email,
            password=password,
            display_name=display_name,
            last_name=last_name,
        ),  # type: ignore
        "email": email,
        "password": password,
        "display_name": display_name,
        "last_name": last_name,
    }


@pytest.fixture
def new_user(db):
    email = faker.email()
    password = faker.password()
    display_name = faker.name_nonbinary()
    last_name = faker.last_name()
    return {
        "user": User.objects.create_user(
            email=email,
            password=password,
            display_name=display_name,
            last_name=last_name,
        ),  # type: ignore
        "email": email,
        "password": password,
        "display_name": display_name,
        "last_name": last_name,
    }


@pytest.fixture
def household_name():
    return faker.last_name() + " Household"


@pytest.fixture
def household(db, user):
    h_name = user["last_name"] + " Household"
    household = Household.objects.create(name=h_name, created_by=user["user"])
    HouseholdMember.objects.create(
        user=user["user"],
        household=household,
        member_type=HouseholdMember.MemberType.ADMIN,
    )
    return {
        "name": h_name,
        "household": household,
    }


@pytest.mark.django_db
class TestHouseholdModel:
    def test_create_household(self, user, household_name):
        h = Household.objects.create(name=household_name, created_by=user["user"])
        result = cast(Household, Household.objects.first())
        assert result is not None
        assert h == result
        assert household_name == h.name
        assert user["user"] == result.created_by
        assert isinstance(result.uuid, uuid.UUID)


@pytest.mark.django_db
class TestHouseholdList:
    def test_unauthenticated_redirected_to_login(self, client):
        response = client.get(reverse("households:index"))
        assert response.status_code == 302
        response = client.get(reverse("households:index"), follow=True)
        assert "login" in response.redirect_chain[-1][0]

    def test_authenticated_gets_page(self, client, user):
        logged_in = client.login(email=user["email"], password=user["password"])
        assert logged_in
        response = client.get(reverse("households:index"))
        assert "Your Household" in response.content.decode("utf-8")

    def test_no_households_prompt_to_create(self, client, user):
        logged_in = client.login(email=user["email"], password=user["password"])
        assert logged_in
        response = (
            client.get(reverse("households:index")).content.decode("utf-8").lower()
        )
        assert "create a household" in response


@pytest.mark.django_db
class TestHouseholdCreate:
    def test_unauthenticated_redirected_to_login(self, client):
        response = client.get(reverse("households:create"))
        assert response.status_code == 302
        response = client.get(reverse("households:create"), follow=True)
        assert "login" in response.redirect_chain[-1][0]

    def test_create_page_has_form(self, client, user):
        client.login(email=user["email"], password=user["password"])
        response = client.get(reverse("households:create"))
        assert isinstance(response.context["form"], HouseholdCreateForm)

    def test_create_household_has_admin_member(self, client, user, household_name):
        client.login(email=user["email"], password=user["password"])
        h = Household.objects.first()
        assert h is None
        response = client.post(
            reverse("households:create"),
            data={"name": household_name},
            follow=True,
        )
        h = cast(Household, Household.objects.first())
        assert h is not None
        assert h.name == household_name
        hm = cast(HouseholdMember, HouseholdMember.objects.first())
        assert hm.user == user["user"]
        assertRedirects(response, reverse("households:index"))
        assertContains(response, household_name)


@pytest.mark.django_db
class TestHouseholdDetail:
    def test_unauthenticated_redirected_to_login(self, client):
        response = client.get(
            reverse(
                "households:detail",
                kwargs={"uuid": uuid.uuid4()},
            )
        )
        assert response.status_code == 302
        response = client.get(
            reverse("households:detail", kwargs={"uuid": uuid.uuid4()}),
            follow=True,
        )
        assert "login" in response.redirect_chain[-1][0]

    def test_authenticated_user_gets_detail_page(self, client, user, household_name):
        client.login(email=user["email"], password=user["password"])
        h = Household.objects.create(name=household_name, created_by=user["user"])
        HouseholdMember.objects.create(
            household=h,
            user=user["user"],
            member_type=HouseholdMember.MemberType.ADMIN,
        )
        response = cast(
            HttpResponse,
            client.get(reverse("households:detail", kwargs={"uuid": h.uuid})),
        )
        assert response.status_code == 200
        assertContains(response, household_name)


@pytest.mark.django_db
class TestDashboardHousehold:
    def test_create_household_on_dashboard_for_no_household(
        self, client: Client, new_user
    ):
        user = new_user
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        assert "add a household" in response.content.decode("utf-8").lower()

    def test_household_shows_for_existing_household(
        self, client: Client, user, household
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        household_uuid = client.session.get("current_household_uuid")
        print(client.session.keys())
        household_name = Household.objects.get(uuid=household_uuid).name
        assert "add a household" not in response.content.decode("utf-8").lower()
        assertContains(response, household_name)
