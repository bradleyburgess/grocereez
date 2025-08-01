from django.contrib import admin

from .models import Household, HouseholdMember


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    fields = ("name",)
    list_display = ("name", "created_by")


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    fields = ("household", "user", "member_type")
    list_display = ("household", "user", "member_type")
    list_filter = ("household", "member_type")
