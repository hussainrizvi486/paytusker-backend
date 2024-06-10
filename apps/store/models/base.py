from django.db import models
from uuid import uuid4


class StoreErrorLogs(models.Model):
    log = models.TextField()

    def __str__(self) -> str:
        return self.log

class BaseModel(models.Model):
    id = models.CharField(
        default=uuid4, unique=True, editable=False, primary_key=True, max_length=10000
    )
    creation = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ModelMedia(models.Model):
    model_name = models.CharField(max_length=999)
    field_id = models.CharField(max_length=999)
    file = models.FileField()
