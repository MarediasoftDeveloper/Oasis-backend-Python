from django.db import models
from ..models import Customer
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Referrals(models.Model):

    referral_code_sender = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invite_sender")
    referral_code = models.CharField(max_length=9, unique=True)
    referral_code_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='invite_getter')
    is_used = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.referral_code_sender.username + "-" + self.referral_code}'