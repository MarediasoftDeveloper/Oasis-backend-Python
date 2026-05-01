import os
from django.core.exceptions import ValidationError
from django.db import models
from .menu_categories import Food_Menu_Category


def venue_file_upload_path(instance, filename):
    return f'uploads/{instance.menu_category}/menu/{filename}'

def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File too large (max 5MB)")


def validate_menu_file(file):
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.webp', '.heic', '.heif', '.avif', '.bmp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError('Only PDF and image files are allowed.')

class Menu_Items(models.Model):
    item_image = models.ImageField(upload_to=venue_file_upload_path, null=True, blank=True)
    menu_file = models.FileField(
        upload_to=venue_file_upload_path,
        validators=[validate_menu_file, validate_file_size],
        null=True,
        blank=True
    )
    menu_category = models.ForeignKey(Food_Menu_Category, on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    item_name = models.CharField(max_length=150,null=True, blank=True)
    item_description = models.CharField(max_length=800, null=True, blank=True)
    item_specifications = models.CharField(max_length=80, null=True, blank=True)
    item_quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    item_points = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}" 