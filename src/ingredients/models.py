from django.db import models

from base.models import BaseModel
from households.models import Household


class IngredientsCategory(BaseModel):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=300, blank=True, null=True)
    household = models.ForeignKey(
        Household,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_system = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta:  # type: ignore
        unique_together = ("name", "household")
