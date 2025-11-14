from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Customer_profile, Customer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.models.venue_info import Venue_Info

class Oasis_Home(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_info, _ = Customer_profile.objects.get_or_create(customer=user)
        info_serializer = CustomerProfileSerializer(user_info, context={'request': request})
        password_created = user.is_verified and user.has_usable_password()



        return Response({**info_serializer.data, 'is_verified':password_created})
