from django.db import models

from base.models import BaseModel
from households.models import Household


class IngredientsCategory(BaseModel):
    name = models.CharField(
        verbose_name="Name",
        max_length=40,
    )
    description = models.TextField(
        verbose_name="Description",
        max_length=300,
        blank=True,
        null=True,
    )
    household = models.ForeignKey(
        verbose_name="Household",
        to=Household,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_system = models.BooleanField(
        verbose_name="System Value",
        default=False,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:  # type: ignore
        unique_together = ("name", "household")
        verbose_name_plural = "Ingredient Categories"
