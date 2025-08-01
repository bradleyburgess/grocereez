from typing import cast

from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
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


@pytest.mark.django_db
class TestIngredientDelete:
    def test_can_delete_ingredients(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        uuid = ingredient.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:delete-ingredient",
                    kwargs={"uuid": uuid},
                )
            ),
        )
        assertRedirects(response, reverse("ingredients:ingredients-list"))
        with pytest.raises(Ingredient.DoesNotExist):
            Ingredient.objects.get(uuid=uuid)

    def test_delete_forbidden_not_household_user(
        self,
        client: Client,
        user,
        new_user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=new_user["email"], password=new_user["password"])
        uuid = ingredient.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:delete-ingredient",
                    kwargs={"uuid": uuid},
                )
            ),
        )
        assert isinstance(response, HttpResponseForbidden)

    def test_ingredient_delete_link_on_page(
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
        assertContains(
            response,
            reverse(
                "ingredients:delete-ingredient",
                kwargs={"uuid": ingredient.uuid},
            ),
        )


@pytest.mark.django_db
class TestIngredientEdit:
    def test_ingredient_list_edit_link_on_page(
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
        assertContains(
            response,
            reverse(
                "ingredients:edit-ingredient",
                kwargs={"uuid": ingredient.uuid},
            ),
        )

    def test_edit_forbidden_not_household_user(
        self,
        client: Client,
        user,
        new_user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=new_user["email"], password=new_user["password"])
        uuid = ingredient.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:edit-ingredient",
                    kwargs={"uuid": uuid},
                ),
                data={"name": "This won't work", "category": ingredients_category.pk},
            ),
        )
        assert isinstance(response, HttpResponseForbidden)

    def test_edit_ingredient_renders_form(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse,
            client.get(
                reverse(
                    "ingredients:edit-ingredient",
                    kwargs={"uuid": ingredient.uuid},
                )
            ),
        )
        assert isinstance(response.context["form"], IngredientForm)
        assertContains(response, ingredient.name)

    def test_edit_ingredient_saves_data(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        new_name = " ".join(faker.words(2))
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:edit-ingredient",
                    kwargs={"uuid": ingredient.uuid},
                ),
                data={
                    "name": new_name,
                    "category": ingredients_category.pk,
                },
            ),
        )
        assertRedirects(response, reverse("ingredients:ingredients-list"))
        ingredient = Ingredient.objects.get(uuid=ingredient.uuid)
        assert ingredient.name == new_name
