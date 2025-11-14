from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer
from app.Serializers.rewards_achiever_serializer import RewardsAchieverSerializer
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from venue.models.venue_info import Venue_Info
from venue.models.badges import BadgesLevel
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.raffles_entry import Raffles_Entry
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
from datetime import timedelta
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from django.db.models import Sum

class VenueDashboard(APIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]

    def get(self, request):
        # Venue info
        venue_profile = Venue_Info.objects.get(venue=request.user)
        venue_serialized = VenueInfoSerializer(venue_profile)

        # Dates
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Querysets
        challenges_qs = Challenge_Achiever.objects.filter(challenge__venue=request.user)
        rewards_qs = Rewards_Achiever.objects.filter(reward__venue=request.user)
        raffles_qs = Raffles_Entry.objects.filter(raffle__venue=request.user)

        # Last 5 items (if less than 5 exist, return what's available)
        challenges_recent = challenges_qs.order_by('-scanned_at')[:5]
        rewards_recent = rewards_qs.order_by('-achieved_at')[:5]
        raffles_recent = raffles_qs.order_by('-joined_at')[:5]

        # Today and Yesterday Counts
        yesterday_scans = challenges_qs.filter(scanned_at__date=yesterday).count()
        today_scans = challenges_qs.filter(scanned_at__date=today).count()

        if yesterday_scans > 0 or today_scans > 0:
            if yesterday_scans==0:
                yesterday_scans=1    
            percentage_change = (today_scans - yesterday_scans) / yesterday_scans * 100
        else:
            percentage_change = None  # Or assign 100% or 0%


        
        weekly_scans = []
        weekly_points_issue = []
        
        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            challenge_by_day = challenges_qs.filter(scanned_at__date=current_day)
            count = challenge_by_day.count()
            weekly_scans.append({
                "day": current_day.strftime("%A"),  # Day name (Monday, Tuesday...)
                "scans": count
            })

            weekly_points_issue.append({
                "day": current_day.strftime("%A"),  # Day name (Monday, Tuesday...)
                "points": sum([item.points_issued for item in challenge_by_day])
            })

        points_issued = challenges_qs.aggregate(points=Sum('points_issued'))
       
        

        return Response({
            **venue_serialized.data,
            "points_issued":points_issued['points'],
            "weekly_scans":weekly_scans,
            "weekly_points_issued":weekly_points_issue,
            "stats": {
                "today_scans": today_scans,
                "yesterday_scans": yesterday_scans,
                "percentage_change": percentage_change,
            },
            "recent_activity": {
                "challenges": ChallengeAchieverSerializer(challenges_recent, many=True).data,
                "rewards": RewardsAchieverSerializer(rewards_recent, many=True).data,
                "raffles": RafflesEntrySerializer(raffles_recent, many=True).data,
            }
        })







