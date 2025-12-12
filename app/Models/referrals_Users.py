from django.db import models
from app.Models.referrals import Referrals
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class ReferralsUsers(models.Model):

    referral = models.ForeignKey(Referrals, on_delete=models.CASCADE)
    code_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referral_user", limit_choices_to={'user_role':'1'})
    used_at = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return f'{self.code_user.username + "-" + self.referral_code}'