from django.db import models
from oasis.settings import AUTH_USER_MODEL
# Create your models here.

class Set_Point_Price(models.Model):
    instructions = models.CharField(
        max_length=200,
        default="Define your desired price below for 1 point in NZ dollar",
        editable=False  # not editable in admin
    )
    point_value_nzd = models.DecimalField(
        max_digits=6, decimal_places=4,
        default=0.01  # 1 point = 0.01 NZD if 100 points = 1 NZD
    )

    def __str__(self):
        return f"1 point = {self.point_value_nzd} NZD"
