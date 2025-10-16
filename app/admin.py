from django.contrib import admin
from .models import Customer, Customer_profile
from .Models.otp_requests import OTP_Code
from .Models.referrals import Referrals
# Register your models here.

admin.site.register(Customer)
admin.site.register(OTP_Code)
admin.site.register(Referrals)
admin.site.register(Customer_profile)