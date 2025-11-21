from django.db import models
from oasis import settings
from .badges import Badges
from .qr_info_model import QR_Info
from .badges import Badges

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('suspended', 'Suspended'),
]

def rewards_file_upload_path(instance, filename):
    return f'uploads/{instance.title}/{filename}'

class Rewards(models.Model):
    image = models.ImageField(upload_to=rewards_file_upload_path, null=True, blank=True)
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'2'}) 
    title = models.CharField(max_length=150) 
    condition = models.CharField(max_length=250, null=True, blank=True) 
    stock = models.PositiveIntegerField(default=50)
    required_points_for_reward=models.PositiveIntegerField(default=50)
    is_approved = models.CharField(max_length=50, choices=STATUS_CHOICES, default='approved')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_ended = models.BooleanField(default=False)
    rewards_for_badge_holder = models.ManyToManyField(Badges)
    

    def __str__(self):
        return self.title   