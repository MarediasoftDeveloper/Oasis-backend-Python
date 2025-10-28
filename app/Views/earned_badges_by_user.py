from rest_framework import generics
from app.Models.earned_badges_by_user import Earned_Badges
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
        return Response({
            "total_badges": count,
            "results": serializer.data
        })
    





class Earned_Badges_By_User_Retrieve(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Earned_Badges_By_User_Serializer

    def get_queryset(self):
        badge_id = self.kwargs.get('pk')
        return Earned_Badges.objects.filter(user=self.request.user, badge_id=badge_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()
        return Response({
            "number_of_badges": count,
            "earned_badge": serializer.data
        })
