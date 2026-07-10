from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.models import Customer
from venue.models.raffles import Raffles
from venue.models.qr_info_model import QR_Info


STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('live', 'Live'),
    ('upcoming', 'Upcoming'),
    ('completed', 'Completed'),
]

WEEKDAYS = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
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
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ManyToManyField(EventCategory, related_name='events_categories')
    organiser_notice = models.CharField(max_length=2000, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='draft')
    total_scans_required = models.PositiveIntegerField(default=3)
    buy_now_link = models.CharField(max_length=1000, null=True, blank=True)
    recurring_weekday = models.CharField(
        max_length=100,
        choices=WEEKDAYS,
        blank=True,
        null=True,
        help_text="List of weekdays (0=Monday, 6=Sunday)"
    )
    recurring_start_time = models.TimeField(null=True, blank=True)
    recurring_end_time = models.TimeField(null=True, blank=True)
    # qr_code = models.ForeignKey(QR_Info, on_delete=models.CASCADE)          
    raffle = models.ForeignKey(Raffles, on_delete=models.CASCADE, null=True, blank=True)          
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conditions = models.CharField(max_length=1000, null=True, blank=True)
    physical_reward = models.CharField(max_length=1000, null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, limit_choices_to={'user_role__in':['2','3','4']}, null=True, blank=True)