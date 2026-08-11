import uuid
from django.db import models
from oasis import settings
from .badge_category import Badge_Category
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from io import BytesIO
from django.core.files import File


def challenge_upload_path(instance, filename):
    return f'media/challenge/{instance.id}/{filename}'

import uuid
import qrcode

from io import BytesIO

from django.conf import settings
from django.core.files import File
from django.db import models

class QR_Info(models.Model):

    class QRType(models.TextChoices):
        CHALLENGE = "challenge", "Challenge"
        TRAIL = "trail", "Trail"

    code = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    qr_type = models.CharField(
        max_length=20,
        choices=QRType.choices,
        default=QRType.CHALLENGE
    )

    qr_image = models.ImageField(
        upload_to=challenge_upload_path,
        blank=True,
        null=True
    )

    is_expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    @property
    def qr_url(self):
        base_url = settings.QR_BASE_URL.rstrip("/")

        if self.qr_type == self.QRType.TRAIL:
            return (
                f"{base_url}/oasis/api/scan/trails/"
                f"{self.code}/"
            )

        # Default/fallback = challenge
        return (
            f"{base_url}/oasis/api/scan/challenges/"
            f"{self.code}/"
        )

    def save(self, *args, **kwargs):
        # Extra safety:
        # if qr_type is None or empty, force challenge.
        if not self.qr_type:
            self.qr_type = self.QRType.CHALLENGE

        # First save generates UUID and DB record.
        super().save(*args, **kwargs)

        if not self.qr_image:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )

            qr.add_data(self.qr_url)
            qr.make(fit=True)

            img = qr.make_image(
                fill_color="#000",
                back_color="#fff"
            )

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            filename = f"{self.code}.png"

            self.qr_image.save(
                filename,
                File(buffer),
                save=False
            )

            super().save(
                update_fields=["qr_image"]
            )

    def __str__(self):
        return f"{self.qr_type} - {self.code}"





#   class QR_Info(models.Model):
#     code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     # winning_points = models.PositiveIntegerField(default=20)
#     qr_image = models.ImageField(upload_to=challenge_upload_path, blank=True, null=True)
#     is_expired = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(null=True, blank=True)

#     def save(self, *args, **kwargs):
#         # Save once to generate UUID and primary key
#         super().save(*args, **kwargs)

#         # Generate QR only if it doesn't exist
#         if not self.qr_image:
#             qr = qrcode.QRCode(
#                 version=1,
#                 error_correction=qrcode.constants.ERROR_CORRECT_H,
#                 box_size=10,
#                 border=4,
#             )
#             qr.add_data(str(self.code))
#             qr.make(fit=True)

#             # Create image with colors
#             img = qr.make_image(fill_color="#000", back_color="#fff")

#             # Save image into memory buffer
#             buffer = BytesIO()
#             img.save(buffer, format="PNG")
#             buffer.seek(0)  # Reset pointer to start

#             # Save to model field
#             filename = f"{self.code}.png"
#             self.qr_image.save(filename, File(buffer), save=False)

#             # Save model again safely
#             super().save(*args, **kwargs)
    
#     def __str__(self):
#         return str(self.code)

  