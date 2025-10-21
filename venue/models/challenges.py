from django.db import models
from oasis import settings
from .badges import Badges
from .qr_info_model import QR_Info




STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('suspended', 'Suspended'),
]




class Challenges(models.Model):
    title = models.CharField(max_length=150) 
    description = models.CharField(max_length=350, null=True, blank=True) 
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    cool_down_hours = models.PositiveIntegerField() 
    daily_cap = models.PositiveIntegerField(help_text="Define how many times a Challenge can be attempted in a day?") 
    starting_date = models.DateField()
    ending_date = models.DateField(null=True, blank=True)
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE)  
    qr_code = models.ForeignKey(QR_Info, on_delete=models.CASCADE)          
    created_at=models.DateField(auto_now_add=True)
    is_approved = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    

    def __str__(self):
        return self.name