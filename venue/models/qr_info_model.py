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


class QR_Info(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # winning_points = models.PositiveIntegerField(default=20)
    qr_image = models.ImageField(upload_to=challenge_upload_path, blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Save once to generate UUID and primary key
        super().save(*args, **kwargs)

        # Generate QR only if it doesn't exist
        if not self.qr_image:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(str(self.code))
            qr.make(fit=True)

            # Create image with colors
            img = qr.make_image(fill_color="#000", back_color="#fff")

            # Save image into memory buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)  # Reset pointer to start

            # Save to model field
            filename = f"{self.code}.png"
            self.qr_image.save(filename, File(buffer), save=False)

            # Save model again safely
            super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.code)

  