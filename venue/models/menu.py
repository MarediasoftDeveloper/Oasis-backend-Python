from django.db import models
from .menu_categories import Food_Menu_Category


def venue_file_upload_path(instance, filename):
    return f'uploads/{instance.menu_category.venue.id}/menu/{filename}'

class Menu_Items(models.Model):
    item_image = models.ImageField(upload_to=venue_file_upload_path, null=True, blank=True)
    menu_category = models.ForeignKey(Food_Menu_Category, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=150)
    item_description = models.CharField(max_length=800)
    item_specifications = models.CharField(max_length=80, null=True, blank=True)
    item_quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_points = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.item_name}-{self.menu_category.name}"