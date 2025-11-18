from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.rewards import Rewards
from app.Models.rewards_achiever import Rewards_Achiever
from venue.Serializers.rewards_serializer import RewardsSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from django.db.models import Count
from rest_framework.response import Response

class Rewards_Crud_for_Venue(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    serializer_class = RewardsSerializer
    
    def get_queryset(self):
        return Rewards.objects.filter(venue=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Serialize the queryset properly
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data     
        rewards = queryset.filter(is_approved='approved').count()
        rewards_redeemed = Rewards_Achiever.objects.filter(reward__in=queryset)

        redeemed_counts = (
            Rewards_Achiever.objects
            .filter(reward__in=queryset)
            .values('reward')
            .annotate(redeemed=Count('id'))
        )
        redeem_map = {item['reward']: item['redeemed'] for item in redeemed_counts}
        for item in data:
            reward_id = item['id']
            item['redeemed'] = redeem_map.get(reward_id, 0)

     

        return Response({
            'rewards':data,
            "summary":{
                "active_rewards": rewards,
                "total_rewards": queryset.count(),
                "redemptions": rewards_redeemed.count(),
            }
        })
    

        
   

    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

    

