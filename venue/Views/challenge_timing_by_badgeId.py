from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from venue.models.challenges import Challenges
from venue.models.badges import Badges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import VenueChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from django.db.models import Count, Sum



class GetChallengeTiming(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
     
        badge = Badges.objects.get(pk=pk)
        print(badge)
        get_challenge = Challenges.objects.get(badge__badge=badge)
        print(get_challenge)
        return Response({"daily_open_time": get_challenge.daily_open_time,
                         "daily_close_time": get_challenge.daily_close_time})
