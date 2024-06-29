from django.db import models
from uuid import uuid4
from apps.auth_user.models import User


class StoreErrorLogs(models.Model):
    log = models.TextField()


class BaseModel(models.Model):
    id = models.CharField(
        default=uuid4, unique=True, editable=False, primary_key=True, max_length=10000
    )
    creation = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
