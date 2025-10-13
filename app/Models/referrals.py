from django.db import models
from .customers import Customer
# Create your models here.

class Referrals(models.Model):

    referral_code_sender = models.ForeignKey(Customer, on_delete=models.CASCADE)
    refferal_code = models.CharField(max_length=150, unique=True)
    refferal_code_user = models.ForeignKey(Customer, on_delete=models.CASCADE)