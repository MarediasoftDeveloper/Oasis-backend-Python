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
from rest_framework.routers import DefaultRouter
from organisers.Views.eventsListRetrieveView import EventsListView, EventsRetrieveView
from organisers.Views.eventPostsCreate import EventPostCreateStaffView
from organisers.Views.eventParticipatingVenues import EventParticipatingVenuesView
from organisers.Views.userJoinEvent import UserJoinEventView


router = DefaultRouter()
router.register(r'events-participating', EventParticipatingVenuesView, basename='events-participating')


urlpatterns = [
    path('events/', EventsListView.as_view(), name='events'),
    path('events/<int:pk>/', EventsRetrieveView.as_view(), name='events-details'),
    path('events-posts/', EventPostCreateStaffView.as_view(), name='events-posts'),
    path('attend-event/', UserJoinEventView.as_view(), name='attend-event'),
    path('', include(router.urls)),

]   
