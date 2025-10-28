from django.db import models
from ..models import Customer
from venue.models.challenges import Challenges
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Challenge_Achiever(models.Model):

    customer_taken = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'user_role':'1'})
    challenge = models.ForeignKey(Challenges, on_delete=models.CASCADE)
    scanned_at = models.DateField(auto_now_add=True,null=True, blank=True)
    scanned_time = models.TimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"earned {self.customer_taken.username}-{self.challenge.title}"
