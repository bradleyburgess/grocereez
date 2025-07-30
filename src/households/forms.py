from django import forms

from .models import Household


class HouseholdCreateForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ("name",)


class AddHouseholdMemberForm(forms.Form):
    email = forms.EmailField(required=True, label="User Email")
    is_admin = forms.BooleanField(
        initial=False, label="Add as admin user", required=False
    )
