from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_and_admin_only_permission import Request_By_Venue_And_Admin_Only
from rest_framework.response import Response
from app.models import Customer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.models.venue_info import Venue_Info
from app.Serializers.customer_signup_serializer import Customer_Serializer



class ProtectedRouteAPI(APIView):

    permission_classes=[IsAuthenticated, Request_By_Venue_And_Admin_Only]

    def get(self, request):
        if self.request.user.user_role=='2':
            get_venue = Venue_Info.objects.get(venue=request.user)
            return Response({
                "venue": VenueInfoSerializer(get_venue).data,
                "user_role":request.user.user_role,
                "is_verified":request.user.is_verified,
            }) 
        

        return Response({
            "admin":Customer_Serializer(request.user).data,
            "user_role":request.user.user_role,
            "is_verified":request.user.is_verified,
        })
        

