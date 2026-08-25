from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from venue.models.rewards import Rewards
from venue.models.badges import Badges
from django.db.models import Q
from django.utils import timezone


class Trail(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    featured_image = models.ImageField(
        upload_to="trails/"
    )
    location = models.CharField(max_length=255)

    instructions = models.TextField(
        null=True,
        blank=True
    )
    historical_information = models.TextField(
        null=True,
        blank=True
    )

    reward = models.ForeignKey(
        Rewards,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trails"
    )
    badge = models.ForeignKey(
        Badges,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trails"
    )
    reward_points = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_trails"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_garden = models.BooleanField(default=False)

    

    def __str__(self):
        return self.title