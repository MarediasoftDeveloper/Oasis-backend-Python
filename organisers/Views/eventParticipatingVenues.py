from rest_framework import viewsets, generics  
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from venue.models.venue_info import Venue_Info
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer, EventBulkVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only



class EventParticipatingVenuesView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    queryset = VenuesParticipatingEvents.objects.all()
    serializer_class = EventAppVenuesParticipatingSerializer    




class EventBulkParticipatingVenuesView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    queryset = VenuesParticipatingEvents.objects.all()
    serializer_class = EventBulkVenuesParticipatingSerializer   


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instances = serializer.save()

        return Response(
            {"message": "Participating venues added successfully."},
            status=status.HTTP_201_CREATED
        )