from django.db import models
from oasis import settings
from venue.models.badge_category import Badge_Category
from .venue_badges import Venue_Badges
from .qr_info_model import QR_Info
from django.utils import timezone
from datetime import time


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('suspended', 'Suspended'),
]
 

def challenge_file_upload_path(instance, filename):
    return f'uploads/challenges/{instance.id}/{filename}'

class Challenges(models.Model):
    image = models.ImageField(upload_to=challenge_file_upload_path, default='media/challenge_default/scan.jpg')
    title = models.CharField(max_length=150) 
    description = models.CharField(max_length=350, null=True, blank=True) 
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'2'}) 
    cool_down_minutes = models.PositiveIntegerField() 
    daily_cap = models.PositiveIntegerField(help_text="Define how many times a Challenge can be attempted in a day?") 
    starting_at = models.DateTimeField()
    ending_at = models.DateTimeField()
    badge = models.ForeignKey(Venue_Badges, on_delete=models.CASCADE)  
    qr_code = models.ForeignKey(QR_Info, on_delete=models.CASCADE)          
    created_at=models.DateTimeField(auto_now_add=True)
    is_approved = models.CharField(max_length=50, choices=STATUS_CHOICES, default='approved')
    is_ended = models.BooleanField(default=False)
    # daily_open_time = models.TimeField()
    # daily_close_time = models.TimeField()
   
    def __str__(self):
        return self.title