from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import HouseholdCreateForm
from .models import Household, HouseholdMember


@login_required
def index(request: HttpRequest) -> HttpResponse:
    households = Household.objects.filter(householdmember__user=request.user)
    context = {"households": households}
    return render(request, "households/index.html", context=context)


@login_required
def create(request: HttpRequest) -> HttpResponse:
    form = HouseholdCreateForm()
    if request.method == "POST":
        form = HouseholdCreateForm(request.POST)
        if form.is_valid():
            h = Household.objects.create(
                name=form.cleaned_data["name"], created_by=request.user
            )
            HouseholdMember.objects.create(
                household=h,
                user=request.user,
                member_type=HouseholdMember.MemberType.ADMIN,
            )
            return redirect(reverse_lazy("households:index"))
    context = {"form": form}
    return render(request, "households/create.html", context=context)


@login_required
def detail(request: HttpRequest, uuid: UUID) -> HttpResponse:
    household = Household.objects.filter(householdmember__user=request.user).get(
        uuid=uuid
    )
    context = {"household": household}
    return render(request, "households/detail.html", context=context)
