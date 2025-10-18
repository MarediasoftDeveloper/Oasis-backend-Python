
from django.db import models
from oasis import settings


class Venue_Opening_Hours(models.Model):
    
    venue = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venue')
    monday = models.CharField(max_length=50)
    tuesday = models.CharField(max_length=50)
    wednesday = models.CharField(max_length=50)
    thursday = models.CharField(max_length=50)
    friday = models.CharField(max_length=50)
    saturday = models.CharField(max_length=50)
    sunday = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.venue:
            self.venue.user_role = '2'
            self.venue.save()  # Save the related venue object
        super().save(*args, **kwargs)

    def __str__(self):
        return self.venue