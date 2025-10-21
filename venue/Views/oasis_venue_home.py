from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.models.venue_info  import Venue_Info 
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from rest_framework import status 

class Oasis_Venue_Home(APIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]

    def get(self, request):
        venue = request.user
        venue_info, _ = Venue_Info.objects.get_or_create(venue=venue)
        info_serializer = VenueInfoSerializer(venue_info, context={'request': request})

        if info_serializer.data.get('status') == 'pending':
            return Response({"error":"Your account is pending for approval!"}, status=status.HTTP_401_UNAUTHORIZED)


        return Response({
            'user': {
                'id': venue.id,
                'email': venue.email,
                **info_serializer.data  # merge serialized profile data safely
            }
        }, status=status.HTTP_200_OK)
