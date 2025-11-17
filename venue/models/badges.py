from django.db import models
from oasis import settings
from .badge_category import Badge_Category




from django.db import models
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import os

@deconstructible
class SVGAndImageValidator:
    def __call__(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.avif','.jpg', '.jpeg', '.png', '.gif', '.svg']
        if ext not in valid_extensions:
            raise ValidationError(f'Unsupported file extension: {ext}. Allowed: {", ".join(valid_extensions)}')

class SVGAndImageField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [SVGAndImageValidator()]
        super().__init__(*args, **kwargs)





class Badges(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True) 
    


    def __str__(self):
        return self.name + f"-{self.id}"
    


    


class BadgesLevel(models.Model):
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE)
    image = SVGAndImageField(upload_to='media/badges/')
    category = models.ForeignKey(Badge_Category, on_delete=models.CASCADE)  
    points_per_task = models.PositiveIntegerField(default=20)


    def __str__(self):
        return self.badge.name + f"-{self.badge.id}-" + self.category.category