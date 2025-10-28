from rest_framework.views import APIView
from venue.models.venue_badges import Venue_Badges
from venue.Serializers.venue_badges_serializer import VenueBadgesSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from app.models import Customer
from venue.models.venue_info import Venue_Info
from rest_framework.response import Response

class Venue_Badge_CRUD(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        venues = Customer.objects.filter(user_role='2')
        data = []

        for venue in venues:
            # Get the related Venue_Info and all Venue_Badges for this venue
            venue_info = Venue_Info.objects.filter(venue=venue).first()
            venue_badges = Venue_Badges.objects.filter(venue=venue)

            # Serialize each part
            venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
            venue_badges_data = VenueBadgesSerializer(venue_badges, many=True).data

            # Append to the main list
            data.append({
                "venue_profile": venue_info_data,
                "venue_badges": venue_badges_data
            })

        return Response(data)

 
 
class Venue_Badge_CRUD_Retrieve(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, venue_id):
        venue = Customer.objects.get(id=venue_id, user_role='2')
        data = []
        venue_info = Venue_Info.objects.filter(venue=venue).first()
        venue_badges = Venue_Badges.objects.filter(venue=venue)


        # Serialize each part
        venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
        venue_badges_data = VenueBadgesSerializer(venue_badges, many=True).data

        # Append to the main list
        data.append({   
            "venue_profile": venue_info_data,
            "venue_badges": venue_badges_data
        })

        return Response(data)

 