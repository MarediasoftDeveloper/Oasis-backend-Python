from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.challenges import Challenges
from venue.Serializers.challenge_serializer import ChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly

class Challenges_Crud_for_Venue(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = ChallengesSerializer

    def get_queryset(self):
        return Challenges.objects.filter(venue=self.request.user)

    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

    

