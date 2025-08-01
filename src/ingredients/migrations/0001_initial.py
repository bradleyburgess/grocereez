# Generated by Django 5.2.4 on 2025-07-31 08:54

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("households", "0003_alter_household_uuid_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="IngredientCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=40)),
                (
                    "description",
                    models.TextField(blank=True, max_length=300, null=True),
                ),
                ("is_system", models.BooleanField(default=False)),
                (
                    "household",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="households.household",
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "household")},
            },
        ),
    ]
