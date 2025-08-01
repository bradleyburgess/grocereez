from django.urls import path

from . import views

app_name = "households"

urlpatterns = [
    path("create", views.create, name="create"),
    path("view", views.current_household_detail, name="view-current"),
    path("add-member", views.add_member, name="add-member"),
    path("<uuid:uuid>", views.detail, name="detail"),
    path("", views.index, name="index"),
]
