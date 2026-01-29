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

        # --- TIME SETUP (CORRECT) ---
        now_utc = timezone.now()
        now_local = timezone.localtime(now_utc)

        today = now_local.date()
        yesterday = today - timedelta(days=1)

        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)          # Sunday

        first_day_this_month = today.replace(day=1)
        last_month_date = first_day_this_month - timedelta(days=1)

        # --- USERS ---
        users = Customer.objects.filter(user_role='1')

        # current_month_users = users.filter(
        #     date_joined__year=today.year,
        #     date_joined__month=today.month,
        # )
        # last_month_users = users.filter(
        #     date_joined__year=today.year,
        #     date_joined__month=today.month,
        # )
        # current = current_month_users.count()
        # last = last_month_users.count()
        # users_growth_this_month = ((current - last) / last) * 100 if last > 0 else 100

        now = timezone.now()
        start_30 = now - timedelta(days=30)

        total_now = users.count()

        local_now = timezone.localtime(now)

        start_of_today = local_now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        new_last_30 = users.filter(
            date_joined__gte=start_30,
            date_joined__lte=now,
        ).count()

        today_joined = users.filter(
            date_joined__gte=start_of_today,
            date_joined__lte=local_now,
        ).count()

        total_before_30 = total_now - new_last_30

        users_growth = (
            (new_last_30 / total_before_30) * 100
            if total_before_30 > 0
            else 100
        )

        total_users = {
            "users": total_now,
            "current_day":today_joined,
            "previous": total_before_30,
            "users_growth_this_month": round(users_growth, 2),
        }

        # --- VENUES ---
        venues = Customer.objects.filter(user_role='2')

        # current_month_venues = venues.filter(
        #     date_joined__year=today.year,
        #     date_joined__month=today.month,
        # )
        # last_month_venues = venues.filter(
        #     date_joined__year=last_month_date.year,
        #     date_joined__month=last_month_date.month,
        # )

        # current = current_month_venues.count()
        # last = last_month_venues.count()

        # venue_growth_this_month = ((current - last) / last) * 100 if last > 0 else 100


        total_venues_now = venues.count()

        new_venues_last_30 = venues.filter(
            date_joined__gte=start_30,
            date_joined__lte=now,
        ).count()

        total_venues_before_30 = total_venues_now - new_venues_last_30

        venue_growth_this_month = (
            (new_venues_last_30 / total_venues_before_30) * 100
            if total_venues_before_30 > 0
            else 100
        )
        venues_today_joined = venues.filter(
            date_joined__gte=start_of_today,
            date_joined__lte=local_now,
        ).count()
        
        total_venues = {
            "venues": total_venues_now,
            "previous": total_venues_before_30,
            "current_day": venues_today_joined,
            "venue_growth_this_month": round(venue_growth_this_month, 2),
        }

        # --- SCANS (LOCAL DATE) ---
        today_scans = Challenge_Achiever.objects.filter(
            scanned_at__date=today
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
            "total_scans_today": today_scans,
            "scan_growth": round(scan_growth, 2),
        }

        # --- BADGES (LOCAL WEEK) ---
        total_earned_badges = Earned_Badges.objects.count()

        current_week_earned_badges = Earned_Badges.objects.filter(
            date__date__range=[start_of_week, end_of_week]
        ).count()

        badges_data = {
            "total_badges": total_earned_badges,
            "current_week_earned_badges": current_week_earned_badges,
        }

        # --- POINTS ---
        points_in_circulation = Customer_profile.objects.aggregate(
            circulation_points=Sum("total_redeemed_points")
        )

        # --- LOGGED IN USERS (UTC LOGIC – CORRECT) ---
        logged_in_users = OutstandingToken.objects.filter(
            expires_at__gte=now_utc,
            user__user_role='1'
        ).values("user_id").distinct().count()

        # --- WEEKLY SCANS / POINTS (LOCAL DATE) ---
        weekly_scans = []
        weekly_points_issue = []

        for i in range(7):
            current_day = today - timedelta(days=i)

            challenge_by_day = Challenge_Achiever.objects.filter(
                scanned_at__date=current_day
            )

            weekly_scans.append({
                "day": current_day.strftime("%A"),
                "scans": challenge_by_day.count(),
            })

            weekly_points_issue.append({
                "day": current_day.strftime("%A"),
                "points": sum(item.points_issued for item in challenge_by_day),
            })

        weekly_scans.reverse()
        weekly_points_issue.reverse()

        # --- LATEST VENUES ---
        venue_profiles = (
            Venue_Info.objects
            .select_related("venue")
            .order_by("-venue__date_joined")[:10]
        )

        venue_serialized = VenueInfoStaffSerializer(venue_profiles, many=True)

        return Response({
            "total_users": total_users,
            "total_venues": total_venues,
            "scans_data": scans_data,
            "badges_data": badges_data,
            "points_in_millions": points_in_circulation["circulation_points"],
            "loggedIn_users": logged_in_users,
            "weekly_scans": weekly_scans,
            "weekly_points_issue": weekly_points_issue,
            "venues": venue_serialized.data,
        })




