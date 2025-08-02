from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from households.middleware import HttpRequestWithHousehold
from .models import Recipe


@login_required
def recipes_list(request: HttpRequestWithHousehold) -> HttpResponse:
    household = request.household
    recipes = Recipe.objects.filter(household=household)
    context = {"recipes": recipes}
    return render(request, "recipes/list.html", context=context)
