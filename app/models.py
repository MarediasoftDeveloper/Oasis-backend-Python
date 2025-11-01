from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from oasis.settings import AUTH_USER_MODEL

USER_ROLES =[
    ('1', 'customer'),
    ('2', 'venue'),
    ('3', 'staff'),
]

GENDERS =[
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

def customer_upload_path(instance, filename):
    return f'media/customer/{instance.customer.id}-{instance.customer.username}/{filename}'


class Customer(AbstractUser):

    username = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email =   models.EmailField(unique=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    user_role = models.CharField(max_length=15, choices=USER_ROLES, default='1')
    is_verified = models.BooleanField(default=False)
    

    USERNAME_FIELD = 'username'        # 🔹 use email for login
    REQUIRED_FIELDS = ['email']            # 🔹 no extra required fields



    def __str__(self):
        return str(self.id) + "-" + self.email
    
class Customer_profile(models.Model):

    customer = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    profile_picture = models.ImageField(upload_to=customer_upload_path, null=True, blank=True, default="media/user_default_img/user.png")
    bio = models.CharField(max_length=500, null=True, blank=True)
    is_private = models.BooleanField(default=False)
    age= models.PositiveIntegerField(null=True, blank=True)
    gender= models.CharField(max_length=12, choices=GENDERS, null=True, blank=True)
    total_redeemed_points = models.PositiveIntegerField(default=0)




