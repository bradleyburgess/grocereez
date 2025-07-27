from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/dashboard.html")


def home_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(reverse_lazy("dashboard:index"))
    return render(request, "pages/index.html")
