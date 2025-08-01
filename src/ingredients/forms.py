from typing import Any
from django import forms

from households.models import Household
from .models import IngredientsCategory, Ingredient


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


class IngredientForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=None)

    def __init__(self, household: Household, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = IngredientsCategory.objects.filter(  # type: ignore
            household=household
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["name"] = cleaned_data["name"].strip()
        return cleaned_data

    class Meta:
        model = Ingredient
        fields = ("name", "category")
