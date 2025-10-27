from django.db import models
from oasis import settings

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
]

class Friendships(models.Model):

    request_sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'1'}, related_name='user_send_request')
    request_getter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'1'}, related_name='user_get_request')
    send_on = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    accept_or_declined_on = models.DateField(blank=True, null=True)



