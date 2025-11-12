from django.db import models
from oasis import settings


SOCIAL_MEDIA = (
    ('facebook', 'Facebook'),
    ('instagram', 'Instagram'),
    ('twitter', 'Twitter'),
    ('tiktok', 'TikTok'),
    ('youtube', 'Youtube'),
)

class Social_Media_Accounts(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    social_media = models.CharField(max_length=30, choices=SOCIAL_MEDIA)
    link = models.CharField(max_length=800)

    def __str__(self):
        return f'{self.user.username}-{self.social_media} link'
