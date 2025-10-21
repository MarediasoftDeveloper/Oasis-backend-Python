
from django.db import models
from oasis import settings


class Venue_Opening_Hours(models.Model):
    
    venue = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venue')
    monday = models.CharField(max_length=50, help_text="if closed so write closed else mention timings")
    tuesday = models.CharField(max_length=50,help_text="if closed so write closed else mention timings")
    wednesday = models.CharField(max_length=50, help_text="if closed so write closed else mention timings")
    thursday = models.CharField(max_length=50, help_text="if closed so write closed else mention timings")
    friday = models.CharField(max_length=50, help_text="if closed so write closed else mention timings")
    saturday = models.CharField(max_length=50, help_text="if closed so write closed else mention timings")
    sunday = models.CharField(max_length=50,help_text="if closed so write closed else mention timings")

    def save(self, *args, **kwargs):
        if self.venue:
            self.venue.user_role = '2'
            self.venue.save()  # Save the related venue object
        super().save(*args, **kwargs)

    def __str__(self):
        return self.venue