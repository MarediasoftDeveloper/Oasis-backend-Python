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
from staff.Views.admin_dashboard import AdminDashboardAPI
from staff.Views.venues_data import VenuesDataAPI, VenueRetrieveAPI
from staff.Views.users_data import UsersDataAPI, UserRetrieveAPI



urlpatterns = [
    path('admin-dashboard/', AdminDashboardAPI.as_view(), name='admin-dashboard'),
    path('venue-data/', VenuesDataAPI.as_view(), name='venue-data'),
    path('venue-data/<int:venue_id>/', VenueRetrieveAPI.as_view(), name='venue-data-retrieve'),

    path('user-data/', UsersDataAPI.as_view(), name='user-data'),
    path('user-data/<int:customer_id>/', UserRetrieveAPI.as_view(), name='user-data-retrieve'),
]   
