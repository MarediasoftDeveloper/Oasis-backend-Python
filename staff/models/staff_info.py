from django.db import models
from oasis.settings import AUTH_USER_MODEL
# Create your models here.


class Staff_Info(models.Model):
    staff_user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_role':'3'} , related_name="staff_info")
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='staff/profile_pics/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.venue:
            self.staff_user.user_role = '3'
            self.staff_user.save()  # Save the related venue object
        super().save(*args, **kwargs)