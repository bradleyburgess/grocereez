from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from households.middleware import HttpRequestWithHousehold
from .forms import IngredientsCategoryCreateForm, IngredientsCategoryDeleteForm
from .models import IngredientsCategory


@login_required
def create_category(request: HttpRequestWithHousehold) -> HttpResponse:
    form = IngredientsCategoryCreateForm()
    if request.method == "POST":
        form = IngredientsCategoryCreateForm(request.POST)
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
            ic.delete()
            return redirect(reverse_lazy("ingredients:categories-list"))
    context = {"form": form, "category": ic.name}
    return render(request, "ingredients/categories_delete.html", context=context)


@login_required
def edit_category(request: HttpRequestWithHousehold, uuid: UUID) -> HttpResponse:
    ic = get_object_or_404(IngredientsCategory, uuid=uuid)
    form = IngredientsCategoryCreateForm(instance=ic)
    if request.method == "POST":
        if ic.household != request.household:
            return HttpResponseForbidden(
                "You do not have permission to edit this category"
            )
        form = IngredientsCategoryCreateForm(request.POST)
        if form.is_valid():
            ic.name = form.cleaned_data["name"]
            ic.description = form.cleaned_data["description"]
            ic.save()
            return redirect(reverse_lazy("ingredients:categories-list"))
    context = {"form": form, "category": ic}
    return render(request, "ingredients/categories_edit.html", context=context)
