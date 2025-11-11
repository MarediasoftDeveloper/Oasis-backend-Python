from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.challenges import Challenges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import ChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly

class Challenges_Crud_for_Venue(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = ChallengesSerializer

    def list(self, request, *args, **kwargs):
        challenges = Challenges.objects.filter(venue=self.request.user)
        serialized = self.get_serializer(challenges)
        challenges_active = challenges.filter(is_approved='approved').count()
        challenges_achieved = Challenge_Achiever.objects.filter(challenge__venue=self.request.user)
        total_points_issued = [c.challenge.qr_code.winning_points for c in challenges_achieved]

        print(challenges_active)
        print(total_points_issued)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

    

