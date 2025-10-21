from django.db import models
from oasis import settings






class Food_Menu_Category(models.Model):
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50) 

    def __str__(self):
        return self.name