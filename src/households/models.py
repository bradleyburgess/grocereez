from django.contrib.auth import get_user_model
from django.db import models

from base.models import BaseModel


class Household(BaseModel):
    pass
    name = models.CharField(max_length=150, blank=False, null=False)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
