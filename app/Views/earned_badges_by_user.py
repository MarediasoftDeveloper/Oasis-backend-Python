from rest_framework import generics
from app.Models.earned_badges_by_user import Earned_Badges
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404


class Earned_Badges_By_User(generics.ListAPIView):
    
    permission_classes=[IsAuthenticated]
    serializer_class=Earned_Badges_By_User_Serializer

    def get_queryset(self):
        return Earned_Badges.objects.filter(user=self.request.user)
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()  # 👈 total badges count
        badges_ids = queryset.values_list('badge_id', flat=True)
        earned_badges = BadgesLevel.objects.filter(badge__id__in=badges_ids, category__id=1)
        badges_serialized = BadgesLevelSerializer(earned_badges, many=True)
        return Response({
            "total_badges": count,
            "results": badges_serialized.data
        })
    





class Earned_Badges_By_User_Retrieve(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Earned_Badges_By_User_Serializer

    def get_queryset(self):
        badge_id = self.kwargs.get('pk')
        return Earned_Badges.objects.filter(user=self.request.user, badge_id=badge_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        badge_id = self.kwargs.get('pk')
        earned_badges = BadgesLevel.objects.filter(badge__id=badge_id, category__id=1).first()
        badges_serialized = BadgesLevelSerializer(earned_badges)
        return Response({
            "number_of_badges": count,
            "earned_badge": badges_serialized.data
        })
