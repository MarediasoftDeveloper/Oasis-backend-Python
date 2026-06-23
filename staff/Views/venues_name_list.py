from rest_framework import generics
from venue.models.venue_info import Venue_Info
from staff.Serializers.venue_name_serializer import VenueNameListSerializer
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only
from rest_framework.permissions import IsAuthenticated



class VenueNameList(generics.ListAPIView):
    permission_classes=[IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    queryset = Venue_Info.objects.all()
    serializer_class=VenueNameListSerializer