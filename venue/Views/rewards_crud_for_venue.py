from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.write_by_venue_only import WriteByVenueOnly


class Rewards_Crud_for_Venue(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    serializer_class = RewardsSerializer

    def get_queryset(self):
        return Rewards.objects.filter(venue=self.request.user)

    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

    

