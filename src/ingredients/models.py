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

    def clean(self) -> None:
        super().clean()
        self.name = self.name.strip()
        if self.description:
            self.description = self.description.strip()

    def __str__(self) -> str:
        return self.name

    class Meta:  # type: ignore
        unique_together = ("name", "household")
        verbose_name_plural = "Ingredient Categories"


class Ingredient(BaseModel):
    name = models.CharField(
        verbose_name="Name",
        max_length=40,
    )
    household = models.ForeignKey(
        verbose_name="Household",
        to=Household,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        verbose_name="Category",
        to=IngredientsCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_system = models.BooleanField(
        verbose_name="System Value",
        default=False,
    )

    def clean(self) -> None:
        super().clean()
        self.name = self.name.strip()

    def __str__(self) -> str:
        return self.name

    class Meta:  # type: ignore
        unique_together = ("name", "household", "category")
