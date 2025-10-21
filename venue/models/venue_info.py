from django.db import models
from oasis import settings
# Create your models here.

def venue_file_upload_path(instance, filename):
    return f'uploads/{instance.venue_name}/{filename}'


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('suspended', 'Suspended'),
]

class Venue_Info(models.Model):
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    venue_name = models.CharField(max_length=100)
    venue_logo = models.ImageField(upload_to=venue_file_upload_path, null=True, blank=True)
    venue_cover_photo = models.ImageField(upload_to=venue_file_upload_path, null=True, blank=True)
    address = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=14)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)


    def __str__(self):
        return self.venue_name







