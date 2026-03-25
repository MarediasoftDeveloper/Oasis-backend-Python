from rest_framework.views import APIView
from rest_framework import viewsets, generics
from venue.models.venue_opening_hours import Venue_Opening_Hours
from venue.Serializers.venue_opening_hours_serializer import VenueOpeningHoursSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.response import Response
from rest_framework import status



class Venue_Opening_Hours_View_Staff(viewsets.ModelViewSet):
    queryset = Venue_Opening_Hours.objects.all()
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = VenueOpeningHoursSerializer
    lookup_field = 'venue'
    
    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

    

    def list(self, request, *args, **kwargs):
        # Disable the list view
        return Response(
            {"detail": "Listing all venues is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )