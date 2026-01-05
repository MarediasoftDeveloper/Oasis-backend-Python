from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from venue.models.venue_info import Venue_Info
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework import viewsets 

class Venues_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    queryset = Venue_Info.objects.filter(status="approved")
    serializer_class=VenueInfoSerializer