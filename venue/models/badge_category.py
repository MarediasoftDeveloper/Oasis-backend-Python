from django.db import models
from oasis import settings






class Badge_Category(models.Model):
    category = models.CharField(max_length=50) 
    num_of_task_to_achieve_badge = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.category +"-"+ str(self.num_of_task_to_achieve_badge)
    