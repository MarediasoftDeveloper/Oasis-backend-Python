from django.db import models
from ..models import Customer
from oasis.settings import AUTH_USER_MODEL









class DeviceFCM(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
