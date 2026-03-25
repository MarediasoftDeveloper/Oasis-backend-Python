from django.db import models
from oasis import settings



class UserCurrentAppVersion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    app_version= models.CharField(max_length=250)
    updated_at = models.DateTimeField(auto_now=True)
