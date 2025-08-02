from typing import cast

from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.test import Client
from django.urls import reverse
from faker import Faker
import pytest
from pytest_django.asserts import assertContains, assertRedirects

from households.models import Household

from ..forms import IngredientsCategoryForm
from ..models import IngredientsCategory, Ingredient

faker = Faker()


@pytest.mark.django_db
class TestIngredientCategoryCreate:
    def test_cannot_create_duplicate_category(
        self, ingredients_category: IngredientsCategory
    ):
        i = ingredients_category
        with pytest.raises(IntegrityError):
            IngredientsCategory.objects.create(
                name=i.name, description=i.description, household=i.household
            )

    def test_create_category_form_renders(
        self, client: Client, user, household: Household
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:create-category"))
        )
        assert isinstance(response.context["form"], IngredientsCategoryForm)

    def test_can_add_category(self, client: Client, user, household: Household):
        ic_name = "Fresh Producez"
        client.login(email=user["email"], password=user["password"])
        client.get(reverse("dashboard:index"))
        response = cast(
            HttpResponse,
            client.post(
                reverse("ingredients:create-category"),
                data={
                    "name": ic_name,
                },
            ),
        )
        assert response.status_code == 302
        assert IngredientsCategory.objects.filter(name=ic_name).exists()

    def test_cannot_add_without_household(self, client: Client, new_user):
        user = new_user
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse,
            client.post(
                reverse("ingredients:create-category"), data={"name": "This Won't Work"}
            ),
        )
        assert response.context["form"].errors
        assert any(
            "household" in item for item in response.context["form"].errors["__all__"]
        )


@pytest.mark.django_db
class TestIngredientsCategoryList:
    def test_ingredients_categories_list_has_items(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:categories-list"))
        )
        assertContains(response, ingredients_category.__str__())

    def test_ingredients_categories_list_has_no_items(
        self, client: Client, user, household
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:categories-list"))
        )
        assert not response.context["ingredients_categories"]
        assertContains(response, "no ingredients categories")


@pytest.mark.django_db
class TestIngredientsCategoryDelete:
    def test_can_delete_ingredients_category(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        uuid = ingredients_category.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:delete-category",
                    kwargs={"uuid": uuid},
                )
            ),
        )
        assertRedirects(response, reverse("ingredients:categories-list"))
        with pytest.raises(IngredientsCategory.DoesNotExist):
            IngredientsCategory.objects.get(uuid=uuid)

    def test_delete_forbidden_not_household_user(
        self,
        client: Client,
        user,
        new_user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=new_user["email"], password=new_user["password"])
        uuid = ingredients_category.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:delete-category",
                    kwargs={"uuid": uuid},
                )
            ),
        )
        assert isinstance(response, HttpResponseForbidden)

    def test_ingredients_category_delete_link_on_page(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:categories-list"))
        )
        assertContains(
            response,
            reverse(
                "ingredients:delete-category",
                kwargs={"uuid": ingredients_category.uuid},
            ),
        )

    def test_delete_category_without_delete_ingredients_does_not_delete_ingredients(
        self,
        user,
        client: Client,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        assert IngredientsCategory.objects.exists()
        assert Ingredient.objects.exists()
        client.post(
            reverse(
                "ingredients:delete-category",
                kwargs={
                    "uuid": ingredients_category.uuid,
                },
            ),
            data={"delete_ingredients": False},
        )
        assert not IngredientsCategory.objects.exists()
        assert Ingredient.objects.exists()

    def test_delete_category_with_delete_ingredients_deletes_ingredients(
        self,
        user,
        client: Client,
        household: Household,
        ingredients_category: IngredientsCategory,
        ingredient: Ingredient,
    ):
        client.login(email=user["email"], password=user["password"])
        assert IngredientsCategory.objects.exists()
        assert Ingredient.objects.exists()
        client.post(
            reverse(
                "ingredients:delete-category",
                kwargs={
                    "uuid": ingredients_category.uuid,
                },
            ),
            data={"delete_ingredients": True},
        )
        assert not IngredientsCategory.objects.exists()
        assert not Ingredient.objects.exists()


@pytest.mark.django_db
class TestIngredientsCategoryEdit:
    def test_ingredients_category_list_edit_link_on_page(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse, client.get(reverse("ingredients:categories-list"))
        )
        assertContains(
            response,
            reverse(
                "ingredients:edit-category",
                kwargs={"uuid": ingredients_category.uuid},
            ),
        )

    def test_edit_forbidden_not_household_user(
        self,
        client: Client,
        user,
        new_user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=new_user["email"], password=new_user["password"])
        uuid = ingredients_category.uuid
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:edit-category",
                    kwargs={"uuid": uuid},
                ),
                data={"name": "This won't work", "description": "Neither will this."},
            ),
        )
        assert isinstance(response, HttpResponseForbidden)

    def test_edit_category_renders_form(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        response = cast(
            HttpResponse,
            client.get(
                reverse(
                    "ingredients:edit-category",
                    kwargs={"uuid": ingredients_category.uuid},
                )
            ),
        )
        assert isinstance(response.context["form"], IngredientsCategoryForm)
        assertContains(response, ingredients_category.name)

    def test_edit_category_saves_data(
        self,
        client: Client,
        user,
        household: Household,
        ingredients_category: IngredientsCategory,
    ):
        client.login(email=user["email"], password=user["password"])
        new_name = " ".join(faker.words(2))
        new_description = faker.paragraph(2)
        response = cast(
            HttpResponse,
            client.post(
                reverse(
                    "ingredients:edit-category",
                    kwargs={"uuid": ingredients_category.uuid},
                ),
                data={
                    "name": new_name,
                    "description": new_description,
                },
            ),
        )
        assertRedirects(response, reverse("ingredients:categories-list"))
        ic = IngredientsCategory.objects.get(uuid=ingredients_category.uuid)
        assert ic.name == new_name
        assert ic.description == new_description
