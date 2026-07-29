from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from app.Models.trails.trailModel import Trail
from django.db.models import Q
from django.utils import timezone




class TrailRecord(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trail_records"
    )
    
    trail = models.ForeignKey(
        Trail,
        on_delete=models.CASCADE,
        related_name="records"
    )

    attempt_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )

    flagged = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    points_awarded = models.PositiveIntegerField(default=0)
    reward_awarded = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "trail", "attempt_number"],
                name="unique_user_trail_attempt"
            )
        ]

    def __str__(self):
        return (
            f"{self.user} - {self.trail.title} "
            f"- Attempt {self.attempt_number}"
        )

    @property
    def started(self):
        return self.started_at is not None

    @property
    def completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def total_steps(self):
        return self.trail.steps.count()

    @property
    def completed_steps_count(self):
        return self.step_records.filter(completed=True).count()

    @property
    def progress_percentage(self):
        total = self.total_steps

        if total == 0:
            return 0

        return round(
            self.completed_steps_count / total * 100,
            2
        )

    @property
    def badge_level(self):
        total = self.total_steps

        if total == 0:
            return 0

        completed = self.completed_steps_count
        badge_level_length = self.trail.badge.levels.count()
        return min(
            5,
            completed * int(badge_level_length) // total
        )

    @property
    def suggested_next_step(self):
        completed_step_ids = self.step_records.filter(
            completed=True
        ).values_list("step_id", flat=True)

        return self.trail.steps.exclude(
            id__in=completed_step_ids
        ).order_by("order").first()