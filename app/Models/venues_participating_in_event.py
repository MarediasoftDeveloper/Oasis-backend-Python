from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.models import Customer
from venue.models.venue_info import Venue_Info
from app.Models.events import Events
from oasis import settings
from django.utils import timezone



class VenuesParticipatingEvents(models.Model):
    venues = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    scans_to_achieve_next_tier = models.PositiveIntegerField(null=True, blank=True, help_text="Number of scans to achieve next tier in the selected venue")
    available_from = models.DateTimeField(default=timezone.now, help_text="The date and time from which users can start scanning on this venue")
    available_till = models.DateTimeField(default=timezone.now, help_text="The date and time until which users have to scan on this venue")
    