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
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'badges-category', Badges_Category_Crud, basename='badge_category')
router.register(r'badges', Badges_Crud, basename='badges')
router.register(r'venues-crud', Venues_Crud, basename='venues')


urlpatterns = [
    path('', oasis_venue_home.Oasis_Venue_Home.as_view(), name='home'),
    path('auth/login/', login.Login.as_view(), name='login'),
    path('', include(router.urls))
]   
