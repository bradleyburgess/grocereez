from typing import cast
import uuid

from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertContains

from .forms import HouseholdCreateForm
from .models import Household, HouseholdMember


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
        assert "add a household" in response


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

    def test_cannot_create_household_with_same_name(
        self, client: Client, user, household
    ):
        client.login(email=user["email"], password=user["password"])
        client.get(reverse("dashboard:index"))
        response = cast(
            HttpResponse,
            client.post(reverse("households:create"), data={"name": household["name"]}),
        )
        assert response.status_code == 200
        assertContains(response, "Household with this name already exists")


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
        household_name = household["household"].name
        assert "add a household" not in response.content.decode("utf-8").lower()
        assertContains(response, household_name)
        assertContains(response, "Add a new member")

    def test_view_current_household(self, client: Client, user, household):
        client.login(email=user["email"], password=user["password"])
        client.get(reverse("dashboard:index"))
        client.session.update(
            {"current_household_uuid": str(household["household"].uuid)}
        )
        response = cast(HttpResponse, client.get(reverse("households:view-current")))
        assertContains(response, household["household"].name)


@pytest.mark.django_db
class TestAddMember:
    def test_fails_for_no_existing_user(self, client: Client, user, household):
        household = household["household"]
        client.login(email=user["email"], password=user["password"])
        client.get(reverse("dashboard:index"))
        response = cast(
            HttpResponse,
            client.post(
                reverse("households:add-member"),
                data={"email": "doesnotexist@user.com"},
            ),
        )
        assertContains(response, "User does not exist")

    def test_cannot_add_self(self, client: Client, user, household):
        household = household["household"]
        client.login(email=user["email"], password=user["password"])
        client.get(reverse("dashboard:index"))
        response = cast(
            HttpResponse,
            client.post(
                reverse("households:add-member"),
                data={"email": user["email"]},
            ),
        )
        assert response.status_code == 200
        assertContains(response, "User is already a household member")
