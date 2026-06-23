from rest_framework.permissions import IsAuthenticated, AllowAny
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only
from venue.models.badges import Badges
from rest_framework.response import Response
from staff.Serializers.badge_serializer_staff import BadgesSerializerStaff
from rest_framework import viewsets 

class Badges_Crud_Staff(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    queryset = Badges.objects.all().order_by('-id')
    serializer_class=BadgesSerializerStaff

    