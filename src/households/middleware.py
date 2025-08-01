from typing import Callable
from django.http import HttpRequest, HttpResponse

from .models import Household


class HttpRequestWithHousehold(HttpRequest):
    household: Household | None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class CurrentHouseholdMiddleware:
    def __init__(
        self, get_response: Callable[[HttpRequestWithHousehold], HttpResponse]
    ):
        self.get_response = get_response

    def __call__(self, request: HttpRequestWithHousehold) -> HttpResponse:
        if request.user.is_authenticated:
            uuid = request.session.get("current_household_uuid")
            household = None
            if uuid:
                try:
                    household = Household.objects.get(uuid=uuid)
                except Household.DoesNotExist:
                    pass
            else:
                household = Household.objects.filter(
                    householdmember__user=request.user
                ).first()
                if household:
                    request.session.update(
                        {"current_household_uuid": str(household.uuid)}
                    )

            request.household = household

        response = self.get_response(request)
        return response
