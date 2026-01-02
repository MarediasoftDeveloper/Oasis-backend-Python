from django.db import models
from django.core.exceptions import ValidationError


class PointsPerBadge(models.Model):
    points_per_badge = models.PositiveIntegerField(
        help_text="Value per Badge in points",
        default=20
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and PointsPerBadge.objects.exists():
            raise ValidationError("Only one PointsPricing instance allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"1 badge = {self.points_per_badge} points"
