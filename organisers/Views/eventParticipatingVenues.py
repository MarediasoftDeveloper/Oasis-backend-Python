from rest_framework import viewsets  
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from venue.models.venue_info import Venue_Info
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only



class EventParticipatingVenuesView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_And_Organiser_Only]
    queryset = VenuesParticipatingEvents.objects.all()
    serializer_class = EventAppVenuesParticipatingSerializer    
