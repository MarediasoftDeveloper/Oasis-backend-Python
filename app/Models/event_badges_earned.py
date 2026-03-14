from django.db import models
from oasis import settings
from venue.models.badges import Badges
from venue.models.badges import BadgesLevel
from app.models import Customer
from app.Models.events import Events




class EventBadgesEarned(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, limit_choices_to={'user_role':'1'})
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    points_issued = models.PositiveIntegerField(null=True, blank=True)
    # badge_level = models.ForeignKey(BadgesLevel, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)


