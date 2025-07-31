from django.db import models
from uuid import uuid4


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
