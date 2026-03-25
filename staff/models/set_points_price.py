from django.db import models
from django.core.exceptions import ValidationError


class PointsPricing(models.Model):
    price_per_point = models.PositiveIntegerField(
        help_text="Price per point in NZD cents",
        default=0.01
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and PointsPricing.objects.exists():
            raise ValidationError("Only one PointsPricing instance allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.price_per_point} cents / point"
