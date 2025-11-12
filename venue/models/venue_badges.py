from django.db import models
from oasis import settings
from venue.models.badges import Badges






class Venue_Badges(models.Model):
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'2'})
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.badge.name + " " + self.badge.category.category