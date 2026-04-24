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
from staff.Views.eventStatsExport import EventStatsReportExportView
from staff.Views.venues_data import VenuesDataAPI, VenueRetrieveAPI
from staff.Views.users_data import UsersDataAPI, UserRetrieveAPI
from staff.Views.reports_list import ReportsList, ReportsRUD, ReportsCreate
from staff.Views.challenges_crud_for_staff import Challenges_Crud_for_Staff
from staff.Views.venue_badges_list_challenges import Venue_Badges_retrieve_for_admin, Venue_Badges_list_for_admin
from staff.Views.venues_name_list import VenueNameList
from staff.Views.get_raffles import GetRafflesForAdmin
from staff.Views.raffles_crud_for_staff import Raffles_Crud_for_Staff
from staff.Views.rewards_crud_for_staff import Rewards_Crud_for_Staff
from staff.Views.SellBadges.available_badge_calculation import AvailableBadgesSellCalculation
from staff.Views.venues_crud import Venues_Crud
from staff.Views.OpeningHoursBystaff import Venue_Opening_Hours_View_Staff
from staff.Views.StaffPosts import Post_Crud_Staff, Admin_Post_Crud
from staff.Views.venue_admin_actions import Venue_Info_Approve_Delete
from staff.Views.users_data import UserUpdateDestroyAPI
from staff.Views.users_data import SendNotificationToUser
from staff.Views.referrals_list_staff import ReferralsList
from staff.Views.venues_data import AllPendingVenuesApproved
from staff.Views.friends_of_user_list import GetUserFriendsList
from staff.Views.users_data import AdjustPointsOfUser
from staff.Views.users_data import UserInterestsStaff
from staff.Views.UserStamps import UserStamps
from staff.Views.custom_notification_to_user import SendNotificationToAllUsers
from staff.Views.badges_crud_staff import Badges_Crud_Staff
from staff.Views.badges_level_crud_staff import Badges_Levels_Crud_Staff 
from staff.Views.update_user_create_user import AdminUserListCreateUpdateDelete, AdminDetails, AdminPasswordReset
from staff.Views.eventsCrudStaffView import EventCrudStaffView
from staff.Views.sendNotificationToAttendees import SendNotificationToAttendees
from staff.Views.eventStats import EventStatsView
from staff.Views.events_badge_progress_staff import EventBadgeProgressStaffView
from staff.Views.eventParticipatingVenuesStaffView import EventParticipatingVenuesStaffView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'challenges-crud', Challenges_Crud_for_Staff, basename='challenges-crud')
router.register(r'raffles-crud', Raffles_Crud_for_Staff, basename='raffles-crud-for-staff')
router.register(r'rewards-crud', Rewards_Crud_for_Staff, basename='rewards-crud-staff')
router.register(r'venues-crud-staff', Venues_Crud, basename='venues-crud-staff')
router.register(r'venue-opening-hours-staff', Venue_Opening_Hours_View_Staff, basename='venue-opening-hours-staff')
router.register(r'posts-crud-staff', Post_Crud_Staff, basename='posts-staff')
router.register(r'admin-users-crud', AdminUserListCreateUpdateDelete, basename='admin-users-crud')
router.register(r'badges-crud', Badges_Crud_Staff, basename='badges-crud-staff')
router.register(r'badges-level-crud', Badges_Levels_Crud_Staff, basename='badges-level-crud-staff')
router.register(r'admin-posts-crud-staff', Admin_Post_Crud, basename='admin-crud-posts-staff')
router.register(r'events-crud', EventCrudStaffView, basename='admin-crud-events')


urlpatterns = [
    path('admin-dashboard/', AdminDashboardAPI.as_view(), name='admin-dashboard'),
    path('venue-data/', VenuesDataAPI.as_view(), name='venue-data'),
    path('venue-data/<int:venue_id>/', VenueRetrieveAPI.as_view(), name='venue-data-retrieve'),

    path('user-data/', UsersDataAPI.as_view(), name='user-data'),
    path('user-data/<int:customer_id>/', UserRetrieveAPI.as_view(), name='user-data-retrieve'),
    path('user-update-data/<int:customer_id>/', UserUpdateDestroyAPI.as_view(), name='user-data-update-destroy'),
    path('user-interests/<int:pk>/', UserInterestsStaff.as_view(), name='user-interests-staff'),
    path('user-stamps/<int:pk>/', UserStamps.as_view(), name='user-stamps'),

    path('', include(router.urls)),

    path('admin-data/', AdminDetails.as_view(), name='admin-details'),
    path('admin-password-reset/', AdminPasswordReset.as_view(), name='admin-password-reset'),
    
    path('send-user-notifications/', SendNotificationToUser.as_view(), name='send-notification-to-user'),
    path('send-notifications-all-users/', SendNotificationToAllUsers.as_view(), name='send-notification-to-all-users'),

    path('reports/', ReportsList.as_view(), name='reports'),
    path('reports-create/', ReportsCreate.as_view(), name='reports-create'),
    path('reports/<int:pk>/', ReportsRUD.as_view(), name='reports-update-destroy'),

    path('approve-delete-venue/<int:pk>/', Venue_Info_Approve_Delete.as_view(), name='approve-delete-venue'),
    
    path('venues-name-list/', VenueNameList.as_view(), name='venue-name-list'),

    path('get-raffles-admin/', GetRafflesForAdmin.as_view(), name='get-raffles-admin'),

    path('venue-badges-list/', Venue_Badges_list_for_admin.as_view(), name='venue-badges-list-for-admin'),
    path('all-venues-approved/', AllPendingVenuesApproved.as_view(), name='all-venues-approved'),
    path('venue-badges-list/<int:pk>/', Venue_Badges_retrieve_for_admin.as_view(), name='venue-badges-retrieve-for-challenge'),

    path('referrals-list-staff/', ReferralsList.as_view(), name='referrals-list-staff'),

    path('user-friendships/<int:pk>/', GetUserFriendsList.as_view(), name='get-user-friends'),

    path('sell-badges/', AvailableBadgesSellCalculation.as_view(), name='sell-badges'),

    path('adjust-points-user/', AdjustPointsOfUser.as_view(), name='adjust-points-user'),

    path('notify-attendees/', SendNotificationToAttendees.as_view(), name='notify-attendees'),
    path('event-stats/', EventStatsView.as_view(), name='event-stats'),
    path('event-badges-progress/', EventBadgeProgressStaffView.as_view(), name='event-badge-progress-attendee'),
    path('event-participants/', EventParticipatingVenuesStaffView.as_view(), name='event-participants'),
    path('event-stats-export/', EventStatsReportExportView.as_view(), name='event-stats-report-export'),
]   
