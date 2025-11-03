from django.db import models
from oasis import settings
from .badge_category import Badge_Category





class Badges(models.Model):
    name = models.CharField(max_length=150) 
    category = models.ForeignKey(Badge_Category, on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='media/badges/')
    description = models.CharField(max_length=500, null=True, blank=True) 
    points_per_task = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name + "-" + self.category.category