from django.db.models import TextChoices


class ModelTextChoices(TextChoices):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def to_dict(self) -> dict:
        obj = {}
        if hasattr(self, "choices"):
            for i in self.choices:
                obj[i[0]] = i[1]
        return obj
