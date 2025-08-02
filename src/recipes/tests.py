from typing import List

from django.db.utils import IntegrityError
from faker import Faker
import pytest

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
