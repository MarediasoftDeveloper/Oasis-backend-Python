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
from .Views import google_signup , login, logout, send_invite, rewards_get_retrieve, update_customer_info, raffles_get_retrieve, venue_menu_list
from rest_framework.routers import DefaultRouter
from .Views.oasis_select_interest_crud import Oasis_Select_Interest_CRUD
from .Views.oasis_interests_serializer import Oasis_Interest_CRUD
from .Views.posts_crud import Post_Crud
from .Views.user_stamps import User_Stamps
from .Views.customer_feed import Customer_Feed
from .Views.email.resend_otp import Resent_OTP_For_Email_Verify, Resent_OTP_For_Password_Reset
from .Views.forgot_password import Forgot_Password
from .Views.earned_badges_by_user import Earned_Badges_By_User, Earned_Badges_By_User_Retrieve
from .Views.email.forgot_password_email_validate import Validate_forgot_Password_mail
from .Views.user_badge_records import User_Badges_Record
from .Views.frienships import Friendship_Crud

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'customer-interests', Oasis_Select_Interest_CRUD, basename='customer-interests')
router.register(r'interests', Oasis_Interest_CRUD, basename='interests')
router.register(r'posts', Post_Crud, basename='post_crud')
router.register(r'friendships', Friendship_Crud, basename='friendship_crud')


urlpatterns = [
    path('register/', create_customer.Create_Customer.as_view(), name="Signup"),
    path('registration-complete/<int:pk>/', update_customer.Update_Customer.as_view(), name="update"),
    path('validate-otp/<int:id>/', Validate_mail.as_view(), name="validate-otp"),    
    path('resend-otp/<int:id>/', Resent_OTP_For_Email_Verify.as_view(), name="resent-otp"),    
    path('auth/login/', login.Login.as_view(), name='login'),
    path('auth/logout/', logout.Logout.as_view(), name='logout'),
    
    path('auth/google/', google_signup.Google_Signup.as_view(), name='google-auth'),
   
    path('user/', oasis_home.Oasis_Home.as_view(), name='get_user'),
    path('customer-info/<int:customer>', update_customer_info.Update_Customer_Info.as_view(), name='customer-info'),


    path('send-invite/', send_invite.Send_Invite.as_view(), name='send_invite'), #Invite user and send a refferal code
    

    path('rewards/', rewards_get_retrieve.RewardsGetView.as_view(), name='get-rewards'), #get rewards
    path('rewards/<int:pk>/', rewards_get_retrieve.RewardsRetrieveView.as_view(), name='retrieve-rewards'), #get rewards

    path('raffles/', raffles_get_retrieve.RafflesGetView.as_view(), name='get-raffles'), #get raffles
    path('raffles/<int:pk>/', raffles_get_retrieve.RafflesRetrieveView.as_view(), name='retrieve-raffles'), #get raffles

    path('get-menu-list/<int:pk>/', venue_menu_list.Venue_Menu_List.as_view(), name='venue_menu'), #get raffles
    
    path('feed/', Customer_Feed.as_view(), name='feed'), #get feed
    
    path('forgot-password/', Forgot_Password.as_view(), name='forgot-password'), #forgot password
    path('forgot-password/resent-otp/<int:id>/', Resent_OTP_For_Password_Reset.as_view(), name='forgot-password-resent-otp'), #forgot password
    path('forgot-password/validate-otp/<int:id>/', Validate_forgot_Password_mail.as_view(), name="forgot-password-validate-otp"),    

    path('earned-badges/', Earned_Badges_By_User.as_view(), name="earned-badges"),    
    path('earned-badges/<int:pk>/', Earned_Badges_By_User_Retrieve.as_view(), name="earned-badges-retrieve"),    
    
    path('stamps/', User_Stamps.as_view(), name="stamps"),    
    path('badges-record/<int:id>/', User_Badges_Record.as_view(), name="user_badge_record"),    


    # jwt token 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),  #  Include DRF ViewSet routes
]   
