from django import template
from django.template import RequestContext

from ..models import Household, HouseholdMember

register = template.Library()


@register.simple_tag(takes_context=True)
def user_is_household_admin(context: RequestContext, household: Household):
    try:
        return HouseholdMember.objects.get(
            household=household, user=context["user"]
        ).is_admin()
    except HouseholdMember.DoesNotExist:
        return False
