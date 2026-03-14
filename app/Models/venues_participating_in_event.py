from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.models import Customer
from venue.models.venue_info import Venue_Info
from app.Models.events import Events
from oasis import settings




class VenuesParticipatingEvents(models.Model):
    venues = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    scans_to_achieve_next_tier = models.PositiveIntegerField(null=True, blank=True, help_text="Number of scans to achieve next tier in the selected venue")
    # availabile_till = models.DateTimeField(auto_now_add=True)
    # scan_unique_challenges = models.BooleanField(default=False, help_text="If you have more than 1 number of scans to achieve next tier challenges then check this if you want users to scan unique challenges to achieve next tire else left it uncheck if you don't want keep scans unique")
    