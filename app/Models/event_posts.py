from django.db import models
from oasis import settings
from venue.models.badges import Badges
from app.Models.events import Events
from app.Models.posts import Post
from app.models import Customer
from venue.models.qr_info_model import QR_Info




class EventPosts(models.Model):
    event=models.ForeignKey(Events, on_delete=models.CASCADE)
    posts=models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)