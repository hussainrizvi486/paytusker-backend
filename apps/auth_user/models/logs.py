from django.db import models
from . import User


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    device = models.CharField(max_length=999)

    def __str__(self) -> str:
        return f"{self.user} {self.time}"
