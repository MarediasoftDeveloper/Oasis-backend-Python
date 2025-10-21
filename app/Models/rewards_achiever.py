from django.db import models
from ..models import Customer
from venue.models.rewards import Rewards
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Rewards_Achiever(models.Model):

    customer_taken = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward = models.ForeignKey(Rewards, on_delete=models.CASCADE)
    achieved_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"earned {self.customer_taken.username}-{self.reward.title}"
