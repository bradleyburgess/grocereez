from typing import Any
from django import forms

from .models import IngredientsCategory


class IngredientsCategoryForm(forms.ModelForm):
    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["name"] = cleaned_data["name"].strip()
        return cleaned_data

    class Meta:
        model = IngredientsCategory
        fields = ("name", "description")


class IngredientsCategoryDeleteForm(forms.Form):
    delete_ingredients = forms.BooleanField(
        label="Also delete ingredients",
        required=False,
    )
