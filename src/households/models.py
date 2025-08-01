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

    def user_is_admin(self, user):
        return HouseholdMember.objects.filter(household=self, user=user).exists()

    def clean(self) -> None:
        super().clean()
        self.name = self.name.strip()

    def __str__(self) -> str:
        return self.name


class HouseholdMember(models.Model):
    class MemberType(models.TextChoices):
        MEMBER = "M", "Member"
        ADMIN = "A", "Admin"

    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    member_type = models.CharField(
        max_length=1, choices=MemberType, default=MemberType.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True, editable=False)

    def is_admin(self):
        return self.member_type == HouseholdMember.MemberType.ADMIN

    def __str__(self) -> str:
        return f"{self.user.__str__()} ({self.get_member_type_display()})"  # type: ignore

    class Meta:
        unique_together = ("household", "user")
        verbose_name = "Household Memnber"
        verbose_name_plural = "Household Members"
