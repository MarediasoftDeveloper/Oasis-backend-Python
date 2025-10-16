from django.db import models
from oasis.settings import AUTH_USER_MODEL
# Create your models here.


class Staff_Info(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_info")
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='staff/profile_pics/', null=True, blank=True)