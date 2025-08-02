from typing import cast, List

from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from faker import Faker
import pytest
from pytest_django.asserts import assertContains

from .models import Recipe
from households.models import Household
from ingredients.models import Ingredient

faker = Faker()


@pytest.mark.django_db
class TestRecipesModel:
    def test_can_add_recipe(
        self,
        household: Household,
        ingredient: Ingredient,
    ):
        assert not Recipe.objects.exists()
        name = " ".join(faker.words(2))
        body = "\n\n".join(faker.paragraphs(3))
        r = Recipe.objects.create(name=name, body=body, household=household)
        r.ingredients.set([ingredient])
        r.save()
        assert Recipe.objects.filter(name=name, household=household).exists()

    def test_cannot_add_duplicate(
        self,
        household: Household,
    ):
        name = " ".join(faker.words(2))
        Recipe.objects.create(name=name, household=household)
        with pytest.raises(IntegrityError):
            Recipe.objects.create(name=name, household=household)

    def test_recipe_has_ingredients(
        self,
        household: Household,
        ingredients_list: List[Ingredient],
    ):
        name = " ".join(faker.words(3))
        body = "\n\n".join(faker.paragraphs(3))
        r = Recipe.objects.create(name=name, body=body, household=household)
        assert not r.ingredients.exists()
        r.ingredients.set(ingredients_list)
        r.save()
        assert r.ingredients.count() == len(ingredients_list)


@pytest.mark.django_db
class TestRecipeDashboard:
    def test_recipes_show_on_dashboard(
        self,
        user,
        client: Client,
        ingredients_list: List[Ingredient],
        recipe: Recipe,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        assertContains(response, "1 recipe")
        assertContains(response, recipe.name)

    def test_dashboard_has_recipts_list_link(
        self,
        client: Client,
        user,
        recipe: Recipe,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("dashboard:index")))
        assertContains(response, f'href="{reverse("recipes:list")}"')


@pytest.mark.django_db
class TestRecipeList:
    def test_recipes_list_renders_list(
        self,
        client: Client,
        user,
        household: Household,
        recipe: Recipe,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(HttpResponse, client.get(reverse("recipes:list")))
        assert response.status_code == 200
        assertContains(response, recipe.name)
