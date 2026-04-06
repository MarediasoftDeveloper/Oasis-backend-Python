from rest_framework import viewsets  
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import EventCategory
from organisers.serializers.eventCategorySerializer import EventCategorySerializer
from venue.models.venue_info import Venue_Info
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only



class EventCategoryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer


