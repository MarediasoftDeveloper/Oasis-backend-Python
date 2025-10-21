import uuid
from django.db import models
from oasis import settings
from .badge_category import Badge_Category



def challenge_upload_path(instance, filename):
    return f'media/challenge/{instance.id}/{filename}'


class QR_Info(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    winning_points = models.PositiveIntegerField(default=20)
    qr_image = models.ImageField(upload_to=challenge_upload_path, blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.code