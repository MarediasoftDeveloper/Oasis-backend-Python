from django.db import models
from oasis import settings



class TermsAndConditionsAccept(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    terms_version = models.CharField(max_length=30)
    accepted_at = models.DateTimeField(auto_now_add=True)
