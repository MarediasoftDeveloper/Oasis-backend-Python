from rest_framework import generics
from rest_framework.views import APIView
from app.Serializers.stamps_serializer import StampSerializer
from app.Models.stamps import Stamps
from app.models import Customer_profile
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
import calendar

class StampsCreateView(generics.CreateAPIView):

    permission_classes=[IsAuthenticated, Request_By_Customer_Only]
    serializer_class=StampSerializer

    def get_queryset(self):
        return Stamps.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Safely update user's redeemed points
        profile, created = Customer_profile.objects.get_or_create(customer=self.request.user)
        profile.total_redeemed_points = (profile.total_redeemed_points or 0) + 30
        profile.save()

        # Save stamp with correct user assignment
        serializer.save(user=self.request.user)


    



class StampsListView(APIView):

    permission_classes=[IsAuthenticated, Request_By_Customer_Only]

    def post(self, request):
        current_month = request.data.get('month')
        current_year = request.data.get('year')
        num_days = calendar.monthrange(current_year, current_month)[1]

        stamps = Stamps.objects.filter(
            user=request.user,
            stamped_at__month=current_month,
            stamped_at__year=current_year
        )
        
        stamp_winning_points = 30
        serialized = StampSerializer(stamps, many=True)
        return Response({
            "daily_stamps": serialized.data,
            "collected_stamps": stamps.count(),
            "total_days_in_month": num_days,
            "current_points": stamps.count() * stamp_winning_points,
            "potential_points": stamp_winning_points * num_days
        })

    
    