from django.db import models
from . import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=500)
    image = models.ImageField(null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    digital = models.BooleanField(default=False)

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return f"{self.parent} --> {self.name}"


class ModelMedia(models.Model):
    model_name = models.CharField(max_length=999)
    field_id = models.CharField(max_length=999)
    file = models.FileField()
