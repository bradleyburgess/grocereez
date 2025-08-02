from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from households.middleware import HttpRequestWithHousehold

from .forms import (
    IngredientsCategoryForm,
    IngredientsCategoryDeleteForm,
    IngredientForm,
)
from .models import IngredientsCategory, Ingredient


@login_required
def create_category(request: HttpRequestWithHousehold) -> HttpResponse:
    form = IngredientsCategoryForm()
    if request.method == "POST":
        form = IngredientsCategoryForm(request.POST)
        if form.is_valid():
            household = request.household
            if not household:
                form.add_error(
                    None,
                    "You must add a household before you add an ingredient category",
                )
            else:
                IngredientsCategory.objects.create(
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                    household=household,
                )
                return redirect(reverse_lazy("ingredients:categories-list"))
    context = {"form": form}
    return render(request, "ingredients/categories_create.html", context=context)


@login_required
def categories_list(request: HttpRequestWithHousehold) -> HttpResponse:
    ingredients_categories = IngredientsCategory.objects.filter(
        household=request.household
    )
    context = {"ingredients_categories": ingredients_categories}
    return render(request, "ingredients/categories_list.html", context=context)


@login_required
def delete_category(request: HttpRequestWithHousehold, uuid: UUID) -> HttpResponse:
    form = IngredientsCategoryDeleteForm()
    ic = get_object_or_404(IngredientsCategory, uuid=uuid)
    if ic.household != request.household:
        return HttpResponseForbidden(
            "You do not have permission do delete this category"
        )
    if request.method == "POST":
        form = IngredientsCategoryDeleteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["delete_ingredients"]:
                Ingredient.objects.filter(
                    household=request.household, category=ic
                ).delete()
            ic.delete()
            return redirect(reverse_lazy("ingredients:categories-list"))
    context = {"form": form, "category": ic.name}
    return render(request, "ingredients/categories_delete.html", context=context)


@login_required
def edit_category(request: HttpRequestWithHousehold, uuid: UUID) -> HttpResponse:
    ic = get_object_or_404(IngredientsCategory, uuid=uuid)
    form = IngredientsCategoryForm(instance=ic)
    if request.method == "POST":
        if ic.household != request.household:
            return HttpResponseForbidden(
                "You do not have permission to edit this category"
            )
        form = IngredientsCategoryForm(request.POST)
        if form.is_valid():
            ic.name = form.cleaned_data["name"]
            ic.description = form.cleaned_data["description"]
            ic.save()
            return redirect(reverse_lazy("ingredients:categories-list"))
    context = {"form": form, "category": ic}
    return render(request, "ingredients/categories_edit.html", context=context)


@login_required
def create_ingredient(request: HttpRequestWithHousehold) -> HttpResponse:
    household = request.household
    if not household:
        return render(request, "ingredients/ingredients_create.html")
    form = IngredientForm(household=household)
    if request.method == "POST":
        form = IngredientForm(household=household, data=request.POST)
        if form.is_valid():
            Ingredient.objects.create(
                name=form.cleaned_data["name"],
                category=form.cleaned_data["category"],
                household=household,
            )
            return redirect(reverse_lazy("ingredients:ingredients-list"))
    context = {"form": form}
    return render(request, "ingredients/ingredients_create.html", context=context)


@login_required
def ingredients_list(request: HttpRequestWithHousehold) -> HttpResponse:
    ingredients = Ingredient.objects.filter(household=request.household).order_by(
        "name"
    )
    context = {"ingredients": ingredients}
    return render(request, "ingredients/ingredients_list.html", context=context)


@login_required
def delete_ingredient(request: HttpRequestWithHousehold, uuid: UUID) -> HttpResponse:
    ingredient = get_object_or_404(Ingredient, uuid=uuid)
    if ingredient.household != request.household:
        return HttpResponseForbidden(
            "You do not have permission do delete this category"
        )
    if request.method == "POST":
        ingredient.delete()
        return redirect(reverse_lazy("ingredients:ingredients-list"))
    context = {"ingredient": ingredient}
    return render(request, "ingredients/ingredients_delete.html", context=context)


@login_required
def edit_ingredient(request: HttpRequestWithHousehold, uuid: UUID) -> HttpResponse:
    ingredient = get_object_or_404(Ingredient, uuid=uuid)
    household = request.household
    if ingredient.household != household:
        return HttpResponseForbidden(
            "You do not have permission to edit this ingredient"
        )
    if not household:
        return render(request, "ingredients/ingredients_edit.html")
    form = IngredientForm(household=household, instance=ingredient)
    if request.method == "POST":
        form = IngredientForm(household=household, data=request.POST)
        if form.is_valid():
            ingredient.name = form.cleaned_data["name"]
            ingredient.category = form.cleaned_data["category"]
            ingredient.save()
            return redirect(reverse_lazy("ingredients:ingredients-list"))
    context = {"form": form, "ingredient": ingredient}
    return render(request, "ingredients/ingredients_edit.html", context=context)
