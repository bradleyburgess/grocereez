from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import HouseholdCreateForm, AddHouseholdMemberForm
from .models import Household, HouseholdMember

User = get_user_model()


@login_required
def index(request: HttpRequest) -> HttpResponse:
    households = Household.objects.filter(householdmember__user=request.user)
    context = {"households": households}
    return render(request, "households/index.html", context=context)


@login_required
def create(request: HttpRequest) -> HttpResponse:
    form = HouseholdCreateForm()
    if request.method == "GET":
        form = HouseholdCreateForm(
            initial={"name": request.user.last_name + " Household"}  # type: ignore
        )
    if request.method == "POST":
        form = HouseholdCreateForm(request.POST)
        if form.is_valid():
            household_name = form.cleaned_data["name"].strip()
            if HouseholdMember.objects.filter(
                household__name=household_name, user=request.user
            ):
                form.add_error("name", "Household with this name already exists")
            else:
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
    households = Household.objects.filter(householdmember__user=request.user)
    household = get_object_or_404(households, uuid=uuid)
    members = HouseholdMember.objects.filter(household=household)
    context = {"household": household, "members": members}
    return render(request, "households/detail.html", context=context)


@login_required
def current_household_detail(request: HttpRequest) -> HttpResponse:
    current_household_uuid = request.session.get("current_household_uuid")
    household = Household.objects.filter(householdmember__user=request.user).get(
        uuid=current_household_uuid
    )
    members = HouseholdMember.objects.filter(household=household)
    context = {"household": household, "members": members}
    return render(request, "households/detail.html", context=context)


@login_required
def add_member(request: HttpRequest) -> HttpResponse:
    form = AddHouseholdMemberForm()
    household_uuid = request.session.get("current_household_uuid")
    household = Household.objects.get(uuid=household_uuid)
    if request.method == "POST":
        form = AddHouseholdMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            is_admin = form.cleaned_data["is_admin"]
            try:
                user_to_add = User.objects.get(email=email)
                if HouseholdMember.objects.filter(
                    user=user_to_add, household=household
                ).exists():
                    form.add_error("email", "User is already a household member")
                else:
                    hm = HouseholdMember(household=household, user=user_to_add)
                    if is_admin:
                        hm.member_type = HouseholdMember.MemberType.ADMIN
                    hm.save()
                    return redirect(reverse_lazy("households:view-current"))
            except User.DoesNotExist:
                form.add_error("email", "User does not exist.")
    context = {"form": form, "household": household}
    return render(request, "households/add_member.html", context=context)
