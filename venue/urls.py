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
from .Views import login
from .Views import oasis_venue_home 
from .Views.badges_crud import Badges_Crud 
from .Views.badges_category_crud import Badges_Category_Crud 
from .Views.venues_crud import Venues_Crud
from .Views.rewards_crud_for_venue import Rewards_Crud_for_Venue
from .Views.raffles_crud_for_venue import Raffles_Crud_for_Venue
from .Views.menu_category import Menu_Category_View
from .Views.menu_items import Menu_Items_View
from .Views.venue_opening_hours_crud import Venue_Opening_Hours_View
from .Views.withdraw_raffle import Withdraw_of_Raffle
from .Views.rewards_getter_list import MyRewardsGetView, MyRewardsRetrieveView
from .Views.raffles_getter_list import MyRafflesGetView, MyRafflesRetrieveView
from .Views.venue_badges_crud import Venue_Badge_CRUD, Venue_Badge_CRUD_Retrieve
from .Views.create_venue import Create_Venue
from .Views.challenges_crud_for_venue import Challenges_Crud_for_Venue
from .Views.venue_dashboard import VenueDashboard
from .Views.protected_route_api import ProtectedRouteAPI
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'badges-category', Badges_Category_Crud, basename='badge_category-crud')
router.register(r'badges', Badges_Crud, basename='badges-crud')
router.register(r'venues-crud', Venues_Crud, basename='venues-crud')
router.register(r'rewards-crud', Rewards_Crud_for_Venue, basename='rewards-crud')
router.register(r'raffles-crud', Raffles_Crud_for_Venue, basename='raffles-crud')
router.register(r'challenges-crud', Challenges_Crud_for_Venue, basename='challenges-crud')
router.register(r'menu-items', Menu_Items_View, basename='menu-items')
router.register(r'menu-category', Menu_Category_View, basename='menu-category')
router.register(r'venue-opening-hours', Venue_Opening_Hours_View, basename='venue-opening-hours')
# router.register(r'venue-badges', Venue_Badge_CRUD, basename='venue-badge')


urlpatterns = [
    path('', oasis_venue_home.Oasis_Venue_Home.as_view(), name='home'),
    path('venue-badges/', Venue_Badge_CRUD.as_view(), name='venue-badges'),
    path('venue-badges/<int:venue_id>/', Venue_Badge_CRUD_Retrieve.as_view(), name='venue-badges-retrieve'),
    
    path('auth/login/', login.Login.as_view(), name='login'),
    path('auth/signup/', Create_Venue.as_view(), name='create-venue'),

    path('venue-dashboard/', VenueDashboard.as_view(), name='venue-dashboard'),
    
    path('withdraw-raffle/', Withdraw_of_Raffle.as_view(), name='withdraw-raffle'),
    path('get-my-reward/', MyRewardsGetView.as_view(), name='getmyreward'),
    path('retrieve-my-reward/<int:pk>/', MyRewardsRetrieveView.as_view(), name='retrievemyreward'),

    path('get-my-raffle/', MyRafflesGetView.as_view(), name='getmyraffle'),
    path('retrieve-my-raffle/<int:pk>/', MyRafflesRetrieveView.as_view(), name='retrievemyraffle'),
    path('', include(router.urls)),


    path('protected-route-api/', ProtectedRouteAPI.as_view(), name='protectedrouteapi'),
]   
