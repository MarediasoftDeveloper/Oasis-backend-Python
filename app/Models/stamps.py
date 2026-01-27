from django.db import models
from oasis import settings



class Stamps(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    daily_stamp = models.BooleanField()
    stamped_at = models.DateTimeField(auto_now_add=True)
