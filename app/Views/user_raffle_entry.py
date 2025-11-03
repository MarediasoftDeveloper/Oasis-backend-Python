from rest_framework.views import APIView
from rest_framework import generics
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.raffles_entry import Raffles_Entry
from app.Views.functions.referrals_utils import record_spent_points, deduct_points_to_user
from rest_framework import serializers

class User_Raffles_Entry(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Raffles_Entry.objects.all()
    serializer_class = RafflesEntrySerializer   

    def perform_create(self, serializer):
        raffle = serializer.validated_data.get('raffle')
        user = self.request.user

        # Get required points
        required_points = raffle.points_to_join

        # Deduct points first
        
        deducted = deduct_points_to_user(user, required_points)

        if isinstance(deducted, dict) and deducted.get("error"):
            raise serializers.ValidationError({"error": deducted["error"]})

        record_spent_points(user, required_points)

        # If deduction successful → save entry
        serializer.save(user=user)





