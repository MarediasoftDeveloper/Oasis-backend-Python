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
from django.urls import path, include
from .Views import create_customer, oasis_home, update_customer, use_referral_code
from .Views.email.send_and_validate_email import Validate_mail
from .Views import google_signup , login, logout, send_invite
from rest_framework.routers import DefaultRouter
from .Views.oasis_select_interest_crud import Oasis_Select_Interest_CRUD
from .Views.oasis_interests_serializer import Oasis_Interest_CRUD

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'customer-interests', Oasis_Select_Interest_CRUD, basename='customer-interests')
router.register(r'interests', Oasis_Interest_CRUD, basename='interests')


urlpatterns = [
    path('register/', create_customer.Create_Customer.as_view(), name="Signup"),
    path('registration-complete/<int:pk>/', update_customer.Update_Customer.as_view(), name="update"),
    path('validate-otp/<int:id>/', Validate_mail.as_view(), name="validate-otp"),    
    path('auth/login/', login.Login.as_view(), name='login'),
    path('auth/logout/', logout.Logout.as_view(), name='logout'),
    
    path('auth/google/', google_signup.Google_Signup.as_view(), name='google-auth'),
   
    path('user/', oasis_home.Oasis_Home.as_view(), name='get_user'), #for testing


    path('send-invite/', send_invite.Send_Invite.as_view(), name='send_invite'), #Invite user and send a refferal code
    # path('used-referral-code/', use_referral_code.UseReferralCode.as_view(), name='use_referral_code'), #Invite user and send a refferal code


    # jwt token 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),  #  Include DRF ViewSet routes
]   
