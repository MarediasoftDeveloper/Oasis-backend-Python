from django.db import models

# Create your models here.

class Customer(models.Model):

    username = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=1000, blank=True, null=True)
    is_venue = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + "-" + self.email