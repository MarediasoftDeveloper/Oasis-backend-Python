from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.models import Customer
from app.Models.events import Events




class EventAttendees(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, limit_choices_to={'user_role':'1'})
    joined_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    attended= models.BooleanField(default=False)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)