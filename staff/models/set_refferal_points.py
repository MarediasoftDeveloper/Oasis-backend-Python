from django.db import models
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Set_Refferal_Points(models.Model):
    instructions = models.CharField(
        max_length=200,
        default="Set the desired Points You want Users to win by using refferal code!",
        editable=False  # not editable in admin
    )
    reward_points = models.PositiveBigIntegerField(default=30)

    def __str__(self):
        return f"total refferal winning points = {self.reward_points}"
