from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .models import User

from .forms import CustomUserCreationForm, UserLoginForm


def signup_view(request: HttpRequest) -> HttpResponse:
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            display_name = form.cleaned_data["display_name"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            user = User.objects.create_user(  # type: ignore
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                display_name=display_name,
            )
            login(request, user)
            return redirect(reverse_lazy("dashboard:index"))
    context = {
        "form": form,
    }
    return render(request, "registration/signup.html", context)


def login_view(request: HttpRequest) -> HttpResponse:
    form = UserLoginForm()
    errors = list()
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse_lazy("dashboard:index"))
        errors.append("Invalid credentials")
    return render(
        request, "registration/login.html", context={"form": form, "errors": errors}
    )


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse_lazy("home"))
