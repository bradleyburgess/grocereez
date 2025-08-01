from django.contrib import admin

from .models import IngredientsCategory


@admin.register(IngredientsCategory)
class IngredientsCategoryAdmin(admin.ModelAdmin):
    fields = ("name", "description", "household", "is_system")
    list_display = ("name", "household", "is_system")
    list_filter = ("household", "is_system")
