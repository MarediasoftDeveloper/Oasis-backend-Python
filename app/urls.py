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
from .Views import create_customer, update_customer, use_referral_code
from .Views.email.send_and_validate_email import Send_and_Validate_mail
from .Views import google_signup , login, logout, get_user, send_invite

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', create_customer.Create_Customer.as_view(), name="Signup"),
    path('registration-complete/<int:pk>/', update_customer.Update_Customer.as_view(), name="update"),
    path('sent-validate-otp/<int:id>/', Send_and_Validate_mail.as_view(), name="send-and-validate-otp"),
    path('auth/login/', login.Login.as_view(), name='login'),
    path('auth/logout/', logout.Logout.as_view(), name='logout'),
    
    path('auth/google/', google_signup.Google_Signup.as_view(), name='google-auth'),
   
    path('user/', get_user.Get_User.as_view(), name='get_user'), #for testing


    path('send-invite/', send_invite.Send_Invite.as_view(), name='send_invite'), #Invite user and send a refferal code
    path('used-referral-code/', use_referral_code.UseReferralCode.as_view(), name='use_referral_code'), #Invite user and send a refferal code


    # jwt token 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]   
