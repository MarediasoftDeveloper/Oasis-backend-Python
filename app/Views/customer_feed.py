from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from app.models import Customer_profile

class Customer_Feed(APIView):   

    permission_classes=[IsAuthenticated]

    def get(self, request):
        
        user = request.user
        public_profiles = Customer_profile.objects.filter(customer=user)
        public_profiles_ids = [public_ids.id for public_ids in public_profiles]
        print(public_profiles_ids)


        return Response({"ids":public_profiles_ids})
