from rest_framework.views import APIView
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from app.models import Customer
from venue.models.venue_info import Venue_Info
from rest_framework.response import Response

class Venue_Badge_CRUD(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            venues = Customer.objects.filter(user_role='2')
            data = []
            venue_badges_data=None
            for venue in venues:
                # Get the related Venue_Info and all Venue_Badges for this venue
                venue_info = Venue_Info.objects.filter(venue=venue).first()
                venue_badges = Venue_Badges.objects.filter(venue=venue).distinct().values_list('badge_id', flat=True)
                badges= BadgesLevel.objects.filter(badge__id__in=venue_badges, category__id=1)
                print(badges)
                # Serialize each part
                venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
                if badges:
                    venue_badges_data = BadgesLevelSerializer(badges, many=True).data

                # Append to the main list
                data.append({
                    "venue_profile": venue_info_data,
                    "venue_badges": venue_badges_data or []
                })
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response(data)

 
 
class Venue_Badge_CRUD_Retrieve(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, venue_id):
        try:
            venue = Customer.objects.get(id=venue_id, user_role='2')
            data = []
            venue_info = Venue_Info.objects.filter(venue=venue).first()
            venue_badges = Venue_Badges.objects.filter(venue=venue).distinct().values_list('badge_id', flat=True)
            badges= BadgesLevel.objects.filter(badge__id__in=venue_badges, category__id=1)
            

            print(venue_badges)

            # Serialize each part
            venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
            venue_badges_data = BadgesLevelSerializer(badges, many=True).data

            # Append to the main list
            data.append({   
                "venue_profile": venue_info_data,
                "venue_badges": venue_badges_data
            })
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response(data)

 