from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from venue.models.qr_info_model import QR_Info
from app.Models.trails.trailModel import Trail  
from django.db.models import Q
from django.utils import timezone




class TrailStep(models.Model):
    trail = models.ForeignKey(
        Trail,
        on_delete=models.CASCADE,
        related_name="steps"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    featured_image = models.ImageField(
        upload_to="trail_steps/",
        null=True,
        blank=True
    )
    pin_image = models.ImageField(
        upload_to="trail_step_pins/",
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    qr_code = models.OneToOneField(
        QR_Info,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trail_step"
    )

    step_reward_points = models.PositiveIntegerField(default=0) 


    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["trail", "order"],
                name="unique_step_order_per_trail"
            )
        ]

    def __str__(self):
        return f"{self.trail.title} - {self.title}"