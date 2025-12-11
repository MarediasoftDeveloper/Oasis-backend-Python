
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status, generics, filters
from rest_framework.response import Response
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer
from app.Serializers.rewards_achiever_serializer import RewardsAchieverSerializer
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from app.models import Customer
from app.models import Customer_profile
from venue.models.venue_info import Venue_Info
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import BadgesLevel
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.raffles_entry import Raffles_Entry
from app.Models.earned_badges_by_user import Earned_Badges
from venue.models.venue_badges import Venue_Badges
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import datetime
from datetime import timedelta
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count
from django.db.models import Count, Sum, OuterRef, Subquery, Prefetch
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20         
    page_size_query_param = 'page_size'
    max_page_size = 50

class VenuesDataAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    serializer_class = VenueInfoSerializer
    search_fields = ['venue_name', 'venue__email']

    def get_queryset(self):

        total_scans_subquery = Challenge_Achiever.objects.filter(
            challenge__venue=OuterRef('venue')
        ).values('challenge__venue').annotate(
            total=Count('id')
        ).values('total')

        points_issued_subquery = Challenge_Achiever.objects.filter(
            challenge__venue=OuterRef('venue')
        ).values('challenge__venue').annotate(
            total=Sum('points_issued')
        ).values('total')

        active_badges_subquery = Venue_Badges.objects.filter(
            venue=OuterRef('venue'),
            is_active=True
        ).values('venue').annotate(
            total=Count('id')
        ).values('total')

        return (
            Venue_Info.objects
            .select_related('venue')
            .annotate(
                total_scans=Subquery(total_scans_subquery),
                points_issued=Subquery(points_issued_subquery),
                active_badges=Subquery(active_badges_subquery)
            )
            .order_by('-venue__date_joined')
        )
    
    def list(self, request, *args, **kwargs):
        # ✅ THIS LINE FIXES SEARCH
        queryset = self.filter_queryset(self.get_queryset())

        paginator = self.pagination_class()
        paginated_venues = paginator.paginate_queryset(queryset, request)     

        data = []

        for venue in paginated_venues:
            serialized_venue = VenueInfoSerializer(venue).data

            serialized_venue['total_scans'] = venue.total_scans or 0
            serialized_venue['points_issued'] = venue.points_issued or 0
            serialized_venue['joined_at'] = venue.venue.date_joined
            serialized_venue['active_badges'] = venue.active_badges or 0

            data.append(serialized_venue)

        return paginator.get_paginated_response(data)
    





class VenueRetrieveAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = VenueInfoSerializer
    lookup_field='venue_id'

    def get_queryset(self):

        total_scans_subquery = Challenge_Achiever.objects.filter(
            challenge__venue=OuterRef('venue')
        ).values('challenge__venue').annotate(
            total=Count('id')
        ).values('total')

        points_issued_subquery = Challenge_Achiever.objects.filter(
            challenge__venue=OuterRef('venue')
        ).values('challenge__venue').annotate(
            total=Sum('points_issued')
        ).values('total')

        active_badges_subquery = Venue_Badges.objects.filter(
            venue=OuterRef('venue'),
            is_active=True
        ).values('venue').annotate(
            total=Count('id')
        ).values('total')

        return (
            Venue_Info.objects
            .select_related('venue')
            .annotate(
                total_scans=Subquery(total_scans_subquery),
                points_issued=Subquery(points_issued_subquery),
                active_badges=Subquery(active_badges_subquery)
            )
            .order_by('-venue__date_joined')
        )
    

    def retrieve(self, request, *args, **kwargs):
            venue = self.get_object()

            # ✅ Last 5 scans
            recent_scans = Challenge_Achiever.objects.filter(
                challenge__venue=venue.venue_id
            ).order_by('-scanned_at')[:5]

            # ✅ Last 5 rewards
            recent_rewards = Rewards_Achiever.objects.filter(
                reward__venue=venue.venue_id
            ).order_by('-achieved_at')[:5]

            # ✅ Last 5 raffles
            recent_raffles = Raffles_Entry.objects.filter(
                raffle__venue=venue.venue_id
            ).order_by('-joined_at')[:5]

            data = VenueInfoSerializer(venue).data

            # ✅ Attach computed values safely
            data['total_scans'] = venue.total_scans or 0
            data['points_issued'] = venue.points_issued or 0
            data['active_badges'] = venue.active_badges or 0
            data['joined_at'] = venue.venue.date_joined

            # ✅ Attach related activity
            data['venues_recent_scans'] = ChallengeAchieverSerializer(
                recent_scans, many=True
            ).data

            data['venues_recent_rewards_achieved'] = RewardsAchieverSerializer(
                recent_rewards, many=True
            ).data

            data['venues_recent_raffles_activity'] = RafflesEntrySerializer(
                recent_raffles, many=True
            ).data

            return Response(data)
