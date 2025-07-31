from typing import Any
from django import forms

from .models import Household


class HouseholdCreateForm(forms.ModelForm):
    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["name"] = cleaned_data["name"].strip()
        return cleaned_data

    class Meta:
        model = Household
        fields = ("name",)


class AddHouseholdMemberForm(forms.Form):
    email = forms.EmailField(required=True, label="User Email")
    is_admin = forms.BooleanField(
        initial=False, label="Add as admin user", required=False
    )
