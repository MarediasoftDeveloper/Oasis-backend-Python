from rest_framework import generics
from venue.models.rewards import Rewards
from staff.Serializers.rewards_serializer_staff import GetRewardSerializerStaff
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.write_by_admin_only import WriteByAdminOnly
import django.utils.timezone as timezone






class RewardsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, WriteByAdminOnly]
    serializer_class = GetRewardSerializerStaff
    queryset = Rewards.objects.filter(is_approved='approved', started_at__lte=timezone.now(), ended_at__gte=timezone.now()).order_by('-id')
    