from django.db import models
from oasis import settings



class Customer_Interest(models.Model):
    image = models.ImageField(upload_to='media/interests/', null=True, blank=True)
    category = models.CharField(max_length=200)
    
    def __str__(self):
        return self.category