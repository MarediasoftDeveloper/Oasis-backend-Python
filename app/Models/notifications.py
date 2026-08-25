from django.db import models
from oasis import settings


class Notifications(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=500)
    data = models.JSONField(
        default=dict,
        blank=True
    )
    image = models.URLField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
