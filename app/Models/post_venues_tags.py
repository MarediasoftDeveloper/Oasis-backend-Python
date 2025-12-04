from django.db import models
from oasis import settings
from app.Models.posts import Post
from venue.models.venue_info import Venue_Info

class PostVenueTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="venue_tags")
    venue = models.ForeignKey(Venue_Info, on_delete=models.CASCADE)
    