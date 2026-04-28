from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.models import Customer
from venue.models.qr_info_model import QR_Info


STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('live', 'Live'),
    ('upcoming', 'Upcoming'),
    ('completed', 'Completed'),
]

class EventCategory(models.Model):
    category = models.CharField(max_length=80)
    




class Events(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=3000)
    image = models.ImageField(upload_to='uploads/events')
    location = models.CharField(max_length=500, null=True, blank=True)
    event_start_date = models.DateTimeField()
    event_close_date = models.DateTimeField()
    longitude = models.FloatField(db_index=True, null=True, blank=True)
    latitude = models.FloatField(db_index=True, null=True, blank=True)
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE)
    category = models.ManyToManyField(EventCategory, related_name='events_categories')
    organiser_notice = models.CharField(max_length=2000, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='draft')
    total_scans_required = models.PositiveIntegerField()
    # qr_code = models.ForeignKey(QR_Info, on_delete=models.CASCADE)          
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conditions = models.CharField(max_length=1000, null=True, blank=True)
    physical_reward = models.CharField(max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, limit_choices_to={'user_role__in':['3', '4']}, null=True, blank=True)