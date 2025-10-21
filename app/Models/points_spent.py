from django.db import models
from ..models import Customer
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Points_Spent(models.Model):

    customer = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    points_spent = models.PositiveIntegerField()
    spent_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"spent {self.customer.username}-{self.spent_on}"
