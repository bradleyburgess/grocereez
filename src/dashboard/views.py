from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from households.models import Household, HouseholdMember


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    current_household_uuid = request.session.get("current_household_uuid")
    households = Household.objects.filter(householdmember__user=request.user)
    household = None
    if current_household_uuid:
        household = households.get(uuid=current_household_uuid)
    else:
        household = households.first()
        if household:
            request.session.update({"current_household_uuid": str(household.uuid)})
    members = HouseholdMember.objects.filter(household=household)
    context = {"household": household, "members": members}
    return render(request, "pages/dashboard.html", context=context)


def home_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(reverse_lazy("dashboard:index"))
    return render(request, "pages/index.html")
