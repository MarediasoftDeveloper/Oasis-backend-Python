from django.db import models
from oasis import settings



class UserBlocking(models.Model):
    blockedBy = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blockedBy')
    blockedUser= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blockedUser')
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blockedUser} is blocked by {self.blockedBy}"
