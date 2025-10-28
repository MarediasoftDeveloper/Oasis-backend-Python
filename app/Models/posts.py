from django.db import models
from oasis import settings
import uuid
from .interests import Customer_Interest

def customer_upload_path(instance, filename):
    return f'uploads/{instance.user.id}/{filename}'

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=customer_upload_path)
    caption = models.CharField(max_length=350, null=True, blank=True)
    date = models.DateField(auto_now=True)
    categories = models.ManyToManyField(Customer_Interest, blank=True) 
    slug = models.SlugField(unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            # generate a guaranteed unique slug
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """
        Generate a truly unique slug by checking existing slugs.
        """
        while True:
            slug = uuid.uuid4().hex[:10]
            if not Post.objects.filter(slug=slug).exists(): 
                return slug

    def __str__(self):
        return f"Post by {self.user} ({self.slug})"