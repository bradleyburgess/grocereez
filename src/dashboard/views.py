from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from households.models import HouseholdMember
from households.middleware import HttpRequestWithHousehold

from ingredients.models import IngredientsCategory


@login_required
def dashboard_view(request: HttpRequestWithHousehold) -> HttpResponse:
    household = request.household
    members = HouseholdMember.objects.filter(household=household)
    ingredients_categories = IngredientsCategory.objects.filter(
        household=household
    ).count()
    ingredients = 0
    context = {
        "household": household,
        "members": members,
        "ingredients_categories": ingredients_categories,
        "ingredients": ingredients,
    }
    return render(request, "pages/dashboard.html", context=context)


def home_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(reverse_lazy("dashboard:index"))
    return render(request, "pages/index.html")
