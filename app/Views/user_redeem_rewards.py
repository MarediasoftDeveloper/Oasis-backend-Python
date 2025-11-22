from rest_framework.views import APIView
from rest_framework import generics
from app.Serializers.rewards_achiever_serializer import RewardsAchieverSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.rewards_achiever import Rewards_Achiever
from rest_framework import status
from rest_framework.response import Response
from app.Views.functions.referrals_utils import record_spent_points, deduct_points_to_user
from rest_framework import serializers

class User_Redeem_Rewards(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Rewards_Achiever.objects.all()
    serializer_class = RewardsAchieverSerializer


    def perform_create(self, serializer):
        reward = serializer.validated_data.get('reward')
        user = self.request.user

        required_points = reward.required_points_for_reward

        # Try to deduct points
        deducted = deduct_points_to_user(user, required_points)
        if isinstance(deducted, dict) and deducted.get("error"):
            raise serializers.ValidationError({"error": deducted["error"]})
        
        # Record spending
        record_spent_points(user, required_points)

        # Save reward redemption
        serializer.save(customer_taken=user)
        reward.stock -= 1
        reward.save()
        self.reward_title = reward.title  # store for response message
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        message = f"🎉👏 Congratulations! You redeemed a new reward {self.reward_title}"
        response.data = {"message": message}
        response.status_code = status.HTTP_201_CREATED
        return response


