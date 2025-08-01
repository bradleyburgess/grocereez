from django.urls import path

from . import views

app_name = "ingredients"

ingredients_category_urls = [
    path(
        "categories/create",
        views.create_category,
        name="create-category",
    ),
    path(
        "categories/edit/<uuid:uuid>",
        views.edit_category,
        name="edit-category",
    ),
    path(
        "categories/delete/<uuid:uuid>",
        views.delete_category,
        name="delete-category",
    ),
    path(
        "categories",
        views.categories_list,
        name="categories-list",
    ),
]

ingredient_urls = [
    path(
        "create",
        views.create_ingredient,
        name="create-ingredient",
    ),
    path(
        "",
        views.ingredients_list,
        name="ingredients-list",
    ),
]

urlpatterns = ingredients_category_urls + ingredient_urls
