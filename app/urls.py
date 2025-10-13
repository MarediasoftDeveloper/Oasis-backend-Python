"""
URL configuration for oasis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .Views import create_customer, update_customer
from .Views.email.register_otp_email import Save_otp_Send_mail
from .Views.email.validate_email_otp import Validate_Mail_Otp
from .Views import google_signup , login
urlpatterns = [
    path('register/', create_customer.Create_Customer.as_view(), name="Signup"),
    path('registration-complete/<int:pk>/', update_customer.Update_Customer.as_view(), name="update"),
    path('sent-otp/<int:id>/', Save_otp_Send_mail, name="send-otp"),
    path('validate-otp/<int:id>/', Validate_Mail_Otp, name="validate-otp"),
    path('auth/google/', google_signup.Google_Signup.as_view(), name='google-auth'),
    path('auth/login/', login.Login.as_view(), name='login'),
]   
