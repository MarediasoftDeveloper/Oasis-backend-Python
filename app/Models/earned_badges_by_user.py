from django.db import models
from ..models import Customer
from venue.models.badges import Badges
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Earned_Badges(models.Model):

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE)
    date= models.DateField(auto_now_add=True,null=True, blank=True)
    time= models.TimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user}-{self.badge}"