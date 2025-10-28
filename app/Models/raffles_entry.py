from django.db import models
from oasis import settings
from venue.models.raffles import Raffles


class Raffles_Entry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'user_role':'1'})
    joined_at = models.DateField(auto_now_add=True, null=True, blank=True)
    joined_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    raffle = models.ForeignKey(Raffles, on_delete=models.CASCADE)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}-{self.raffle.title}"