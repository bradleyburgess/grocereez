from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "households/index.html")


@login_required
def create(request: HttpRequest) -> HttpResponse:
    return HttpResponse()
