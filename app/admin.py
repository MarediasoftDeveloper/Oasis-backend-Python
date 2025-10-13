from django.contrib import admin
from .Models.customers import Customer
from .Models.otp_requests import OTP_Code
# Register your models here.

admin.site.register(Customer)
admin.site.register(OTP_Code)