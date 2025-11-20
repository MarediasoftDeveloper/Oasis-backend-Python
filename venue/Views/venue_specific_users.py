from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.raffles_entry import Raffles_Entry
from app.models import Customer_profile, Customer
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.earned_badges_by_user import Earned_Badges
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer
from app.Serializers.rewards_achiever_serializer import RewardsAchieverSerializer 
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from django.db.models import Count, Sum

class VenueSpecificUser(APIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]

    def get(self, request):

        raffle_users = Raffles_Entry.objects.filter(
            raffle__venue=request.user
        ).values_list("user", flat=True).distinct()

        reward_users = Rewards_Achiever.objects.filter(
            reward__venue=request.user
        ).values_list("customer_taken", flat=True).distinct()

        challenge_qs = Challenge_Achiever.objects.filter(
            challenge__venue=request.user
        )

        total_points = challenge_qs.aggregate(total=Sum('points_issued'))['total']


        challenge_users = challenge_qs.values_list("customer_taken", flat=True).distinct()

        # Combine all IDs
        users_set = set(raffle_users) | set(reward_users) | set(challenge_users)

        # Fetch profiles
        user_profiles = Customer_profile.objects.filter(customer__id__in=users_set)

        # Serialize profiles
        data = CustomerProfileSerializer(user_profiles, many=True).data

        
        reward_count_map = dict(
            Rewards_Achiever.objects.filter(
                reward__venue=request.user
            ).values('customer_taken').annotate(count=Count('id')).values_list('customer_taken', 'count')
        )

        challenge_count_map = dict(
            challenge_qs.values('customer_taken')
            .annotate(count=Count('id'))
            .values_list('customer_taken', 'count')
        )

        # Append count to serialized users
        for user in data:
            user_id = user["customer"]["id"]   # or user["id"] depending on serializer
            user["earned_badges"] = Earned_Badges.objects.filter(user__id=user_id).count()
            user["scan_count"] = (
                challenge_count_map.get(user_id, 0)
            )
            user["reward_count"] = (
                reward_count_map.get(user_id, 0)
            )
         

        return Response({"users": data,
                         "total_users":user_profiles.count(),
                         "total_scans":challenge_qs.count(),
                         "total_points":total_points,
                         })



class VenueSpecificUserActivity(APIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]

    def get(self, request, id):
        user = Customer.objects.get(id=id)

        raffles = Raffles_Entry.objects.filter(
            raffle__venue=request.user, user=user
        )

        rewards = Rewards_Achiever.objects.filter(
            reward__venue=request.user, customer_taken=user
        )

        scans = Challenge_Achiever.objects.filter(
            challenge__venue=request.user,customer_taken=user
        )

        raffles_serializer = RafflesEntrySerializer(raffles ,many=True)
        rewards_serializer = RewardsAchieverSerializer(rewards ,many=True)
        challenge_serializer = ChallengeAchieverSerializer(scans ,many=True)

        raffles_data = raffles_serializer.data
        rewards_data = rewards_serializer.data

        # Add title to each raffle
        for r in raffles_data:
            r["title"] = Raffles_Entry.objects.get(id=r["id"]).raffle.title

        # Add title to each reward
        for rw in rewards_data:
            rw["title"] = Rewards_Achiever.objects.get(id=rw["id"]).reward.title


        return Response({
                         "raffles":raffles_data,
                         "scans":challenge_serializer.data,
                         "rewards":rewards_data,   
                         })