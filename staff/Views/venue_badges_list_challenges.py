from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import Badges
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.venue_badges_serializer import VenueBadgesSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.models import Customer
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only

class Venue_Badges_retrieve_for_admin(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]

    def get(self, request, pk):
        try:
            venue_badges = Venue_Badges.objects.filter(venue__id=pk)
            venue_badges_data = VenueBadgesSerializer(venue_badges, many=True)
            

            # Append to the main list
           
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response({"badges":venue_badges_data.data})


class Venue_Badges_list_for_admin(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    
    def get(self, request):
        try:
            badges = Badges.objects.all()
            badges_data = BadgesSerializer(badges, many=True)


            # Append to the main list
           
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response({"badges":badges_data.data})
    