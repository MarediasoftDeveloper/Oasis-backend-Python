from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Serializers.friendship_serializer import FriendshipSerializer
from app.Models.friendships import Friendships
from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q



class Friendship_Crud(viewsets.ModelViewSet):
    queryset = Friendships.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FriendshipSerializer
    
    
    def list(self, request, *args, **kwargs):
        queryset = Friendships.objects.filter(
            Q(request_sender=request.user, status='accepted') | Q(request_getter=request.user, status='accepted')
        )
        serializer = self.get_serializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data)

        return Response({"error_msg":"you have 0 friends!"})
