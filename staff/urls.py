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
from staff.Views.admin_dashboard import AdminDashboardAPI
from staff.Views.venues_data import VenuesDataAPI, VenueRetrieveAPI
from staff.Views.users_data import UsersDataAPI, UserRetrieveAPI
from staff.Views.referral_users_list import ReferralUsersList
from staff.Views.reports_list import ReportsList, ReportsRUD, ReportsCreate
from staff.Views.challenges_crud_for_staff import Challenges_Crud_for_Staff
from staff.Views.venue_badges_list_challenges import Venue_Badges_retrieve_for_admin, Venue_Badges_list_for_admin
from staff.Views.venues_name_list import VenueNameList
from staff.Views.get_raffles import GetRafflesForAdmin
from staff.Views.raffles_crud_for_staff import Raffles_Crud_for_Staff
from staff.Views.rewards_crud_for_staff import Rewards_Crud_for_Staff
from staff.Views.SellBadges.available_badge_calculation import AvailableBadgesSellCalculation

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'challenges-crud', Challenges_Crud_for_Staff, basename='challenges-crud')
router.register(r'raffles-crud', Raffles_Crud_for_Staff, basename='raffles-crud-for-staff')
router.register(r'rewards-crud', Rewards_Crud_for_Staff, basename='rewards-crud')

urlpatterns = [
    path('admin-dashboard/', AdminDashboardAPI.as_view(), name='admin-dashboard'),
    path('venue-data/', VenuesDataAPI.as_view(), name='venue-data'),
    path('venue-data/<int:venue_id>/', VenueRetrieveAPI.as_view(), name='venue-data-retrieve'),

    path('user-data/', UsersDataAPI.as_view(), name='user-data'),
    path('user-data/<int:customer_id>/', UserRetrieveAPI.as_view(), name='user-data-retrieve'),
    path('referrals/', ReferralUsersList.as_view(), name='referrals'),
    path('', include(router.urls)),


    path('reports/', ReportsList.as_view(), name='reports'),
    path('reports-create/', ReportsCreate.as_view(), name='reports-create'),
    path('reports/<int:pk>/', ReportsRUD.as_view(), name='reports-update-destroy'),

    path('venues-name-list/', VenueNameList.as_view(), name='venue-name-list'),
    
    path('get-raffles-admin/', GetRafflesForAdmin.as_view(), name='get-raffles-admin'),

    path('venue-badges-list/', Venue_Badges_list_for_admin.as_view(), name='venue-badges-list-for-admin'),
    path('venue-badges-list/<int:pk>/', Venue_Badges_retrieve_for_admin.as_view(), name='venue-badges-retrieve-for-challenge'),

    path('sell-badges/', AvailableBadgesSellCalculation.as_view(), name='sell-badges'),

]   
