from django.db import models

from base.models import BaseModel
from households.models import Household
from ingredients.models import Ingredient


class Recipe(BaseModel):
    name = models.CharField(max_length=100)
    body = models.TextField()
    ingredients = models.ManyToManyField(
        to=Ingredient,
        related_name="recipes",
    )
    household = models.ForeignKey(
        to=Household,
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    def clean(self) -> None:
        super().clean()
        self.name = self.name.strip()
        if self.body:
            self.body = self.body.strip()

    def __str__(self) -> str:
        return self.name

    class Meta:  # type: ignore
        unique_together = ("name", "household")
