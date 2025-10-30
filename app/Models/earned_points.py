from django.db import models
from ..models import Customer
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Earned_Points(models.Model):

    customer = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'user_role':'1'})
    points_earned = models.PositiveIntegerField()
    earned_on = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return f"earned {self.customer.username}-{self.earned_on}"
