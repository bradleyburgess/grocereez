from django.urls import include

from django.contrib import admin
from django.urls import path

from dashboard.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("registration/", include("users.urls", namespace="users")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("", home_view, name="home"),
]
