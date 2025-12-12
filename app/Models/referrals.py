from django.db import models
from ..models import Customer
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Referrals(models.Model):

    referral_code_sender = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invite_sender", limit_choices_to={'user_role':'1'})
    referral_code = models.CharField(max_length=9, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
   
    def __str__(self):
        return f'{self.referral_code_sender.username + "-" + self.referral_code}'