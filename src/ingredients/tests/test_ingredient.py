from typing import cast

from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from faker import Faker
import pytest
from pytest_django.asserts import assertContains, assertRedirects

from households.models import Household

from ..forms import IngredientForm
from ..models import IngredientsCategory, Ingredient

faker = Faker()


@pytest.mark.django_db
class TestIngredientCreate:
    def test_cannot_create_duplicate(
        self,
        ingredient: Ingredient,
        ingredients_category: IngredientsCategory,
        user,
        household: Household,
    ):
        with pytest.raises(IntegrityError):
            Ingredient.objects.create(
                name=ingredient.name, household=household, category=ingredients_category
            )

    def test_create_form_renders(
        self,
        client: Client,
        household: Household,
        user,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:create-ingredient"))
        )
        assert response.status_code == 200
        assert isinstance(response.context["form"], IngredientForm)

    def test_create_adds_ingredient(
        self,
        client: Client,
        household: Household,
        user,
        ingredients_category: IngredientsCategory,
    ):
        name = faker.name()
        client.login(email=user["email"], password=user["password"])
        assert not Ingredient.objects.filter(name=name).exists()
        response = cast(
            HttpResponse,
            client.post(
                reverse("ingredients:create-ingredient"),
                data={
                    "name": name,
                    "category": ingredients_category.pk,
                },
                follow=True,
            ),
        )
        ingredient = Ingredient.objects.get(name=name)
        assert ingredient.category == ingredients_category
        assert ingredient.household == household
        assertRedirects(response, reverse("ingredients:ingredients-list"))
        assertContains(response, ingredient.name)

    def test_cannot_add_without_household(self, client: Client, new_user):
        user = new_user
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse,
            client.post(
                reverse("ingredients:create-ingredient"),
                data={"name": "This Won't Work"},
            ),
        )
        assert response.status_code == 200
        assert not hasattr(response.context, "form")


@pytest.mark.django_db
class TestDashboardIngredient:
    def test_manage_ingredients_link_on_dashboard(
        self,
        client: Client,
        household: Household,
        ingredients_category: IngredientsCategory,
        user,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        assertContains(response, f'href="{reverse("ingredients:ingredients-list")}"')


@pytest.mark.django_db
class TestIngredientList:
    def test_ingredients_list_has_items(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:ingredients-list"))
        )
        assertContains(response, ingredient.__str__())

    def test_ingredients_categories_list_has_no_items(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:ingredients-list"))
        )
        assert not response.context["ingredients"]
        assertContains(response, "no ingredients")
