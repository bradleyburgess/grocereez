from django.urls import path

from . import views

app_name = "households"

urlpatterns = [
    path("create", views.create, name="create"),
    path("<uuid:uuid>", views.detail, name="detail"),
    path("", views.index, name="index"),
]
