from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from venue.models.qr_info_model import QR_Info
from app.Models.trails.trailModel import Trail  
from django.db.models import Q
from django.utils import timezone




class TrailStepRecord(models.Model):
    trail_record = models.ForeignKey(
        TrailRecord,
        on_delete=models.CASCADE,
        related_name="step_records"
    )
    step = models.ForeignKey(
        TrailStep,
        on_delete=models.CASCADE,
        related_name="completion_records"
    )
    completed = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    qr_verified = models.BooleanField(default=False)
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    flagged_at = models.DateTimeField(
        null=True,
        blank=True
    )
    scanned_longitude = models.DecimalField(
           max_digits=9,
           decimal_places=6,
            null=True,
            blank=True
       )
    scanned_latitude = models.DecimalField(
           max_digits=9,
           decimal_places=6,
            null=True,
            blank=True
       )
   

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trail_record", "step"],
                name="unique_step_per_trail_attempt"
            )
        ]

    def clean(self):
        if (
            self.step_id
            and self.trail_record_id
            and self.step.trail_id != self.trail_record.trail_id
        ):
            raise ValidationError(
                "The selected step does not belong to this trail."
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()

        if self.flagged and self.flagged_at is None:
            self.flagged_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.trail_record.user} - "
            f"{self.step.title}"
        )