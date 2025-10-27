from django.db import models
from oasis import settings
from .interests import Customer_Interest


class User_Interest(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'1'})
    interests = models.ManyToManyField(Customer_Interest, related_name='interests')
    
    def __str__(self):
        return f"{self.user.username}'s profile"