from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer
from app.Serializers.rewards_achiever_serializer import RewardsAchieverSerializer
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from app.models import Customer
from app.models import Customer_profile
from venue.models.venue_info import Venue_Info
from venue.models.badges import BadgesLevel
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.raffles_entry import Raffles_Entry
from app.Models.earned_badges_by_user import Earned_Badges
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
from datetime import timedelta
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from django.db.models import Sum
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from staff.Serializers.venue_info_staff_serializers import VenueInfoStaffSerializer

def format_number_ui(value):
    value = float(value)

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(int(value)) if value.is_integer() else f"{value:.2f}"

class AdminDashboardAPI(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]


    def get(self, request):
        
        users = Customer.objects.filter(user_role='1').order_by('-id')
        now = timezone.now()
        yesterday = now.date() - timedelta(days=1)
        start_of_week = now.date() - timedelta(days=now.date().weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday


        first_day_this_month = now.replace(day=1)
        last_month_date = first_day_this_month - timedelta(days=1)

        current_month_users = users.filter(
            date_joined__year=now.year,
            date_joined__month=now.month,
        )
        last_month_users = users.filter(
            date_joined__year=last_month_date.year,
            date_joined__month=last_month_date.month,
        )
        current = current_month_users.count()
        last = last_month_users.count()

        if last > 0:
            users_growth_this_month = ((current - last) / last) * 100
        else:

            users_growth_this_month = 100  # or 0, depending on your business logic

        total_users = {
            'users':users.count(),
            'users_growth_this_month': round(users_growth_this_month, 2),
        }

        venues = Customer.objects.filter(user_role='2').order_by('-id')
        current_month_venues = venues.filter(
            date_joined__year=now.year,
            date_joined__month=now.month,
        )
        last_month_venues = venues.filter(
            date_joined__year=last_month_date.year,
            date_joined__month=last_month_date.month,
        )
        current = current_month_venues.count()
        last = last_month_venues.count()

        if last > 0:
            venue_growth_this_month = ((current - last) / last) * 100
        else:
            venue_growth_this_month = 100  # or 0, depending on your business logic

        total_venues = {
            'venues':venues.count(),
            'venue_growth_this_month': round(venue_growth_this_month, 2),
        }
        today_scans = Challenge_Achiever.objects.filter(
            scanned_at__date=now.date()
        ).count()

        yesterday_scans = Challenge_Achiever.objects.filter(
            scanned_at__date=yesterday
        ).count()

        
        
        if yesterday_scans > 0:
            scan_growth = ((today_scans - yesterday_scans) / yesterday_scans) * 100
        elif today_scans > 0:
            scan_growth = 100
        else:
            scan_growth = 0
        
        scans_data = {
            'total_scans_today':today_scans,
            'scan_growth':scan_growth,
        }

        total_earned_badges = Earned_Badges.objects.all().count()
        current_week_earned_badges = Earned_Badges.objects.filter(date__date__range=[start_of_week, end_of_week]).count()

        badges_data = {
            'total_badges':total_earned_badges,
            'current_week_earned_badges':current_week_earned_badges,
        }

        points_in_circulation = Customer_profile.objects.all().aggregate(circulation_points=Sum('total_redeemed_points'))

        logged_in_users = OutstandingToken.objects.filter(
            expires_at__gte=timezone.now(), user__user_role='1'
        ).values("user_id").distinct().count()

        

        weekly_scans = []
        weekly_points_issue = []
        
        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            challenge_by_day = Challenge_Achiever.objects.filter(scanned_at__date=current_day)
            count = challenge_by_day.count()
            weekly_scans.append({
                "day": current_day.strftime("%A"),  # Day name (Monday, Tuesday...)
                "scans": count
            })

            weekly_points_issue.append({
                "day": current_day.strftime("%A"),  # Day name (Monday, Tuesday...)
                "points": sum([item.points_issued for item in challenge_by_day])
            })

        venue_profiles = (
            Venue_Info.objects
            .select_related('venue')
            .order_by('-venue__date_joined')[:10]
        )
        venue_serialized = VenueInfoStaffSerializer(venue_profiles, many=True)

     
        return Response({
            "total_users":total_users,
            "total_venues":total_venues,
            "scans_data":scans_data,
            "badges_data":badges_data,
            "points_in_millions": format_number_ui(points_in_circulation['circulation_points']),
            "loggedIn_users":logged_in_users,
            'weekly_scans':weekly_scans,
            'weekly_points_issue':weekly_points_issue,
            'venues':venue_serialized.data,
        })







