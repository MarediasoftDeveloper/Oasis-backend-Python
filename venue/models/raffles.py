from django.db import models
from oasis import settings



class Raffles(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, null=True, blank=True)
    rewards = models.CharField(max_length=250, null=True, blank=True)
    points_to_join = models.PositiveIntegerField()
    rewarded_points = models.PositiveIntegerField(null=True, blank=True, help_text="points will be rewarded to winner (optional)")
    start_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_ended = models.BooleanField(default=False)
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'user_role':'2'})
    num_of_winners = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title