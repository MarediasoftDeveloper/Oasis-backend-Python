from django.db import models
from oasis import settings

def raffle_file_upload_path(instance, filename):
    return f'uploads/{instance.title}/{filename}'

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('suspended', 'Suspended'),
]

class Raffles(models.Model):
    image = models.ImageField(upload_to=raffle_file_upload_path, default='raffle_default/raffle.png')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    rewards = models.CharField(max_length=250, null=True, blank=True)
    points_to_join = models.PositiveIntegerField()
    is_approved = models.CharField(max_length=50, choices=STATUS_CHOICES, default='approved')
    rewarded_points = models.PositiveIntegerField(null=True, blank=True, help_text="points will be rewarded to winner (optional)")
    start_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_ended = models.BooleanField(default=False)
    venue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,limit_choices_to={'user_role':'2'}, null=True, blank=True)
    num_of_winners = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title+"-"+str(self.id)