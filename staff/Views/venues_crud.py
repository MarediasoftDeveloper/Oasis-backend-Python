from rest_framework.permissions import IsAuthenticated, AllowAny
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from venue.models.venue_info import Venue_Info
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework import viewsets 
from django.shortcuts import get_object_or_404

class Venues_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = Venue_Info.objects.all()
    serializer_class=VenueInfoSerializer