from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Serializers.users_interests_serializer import UserInterestSerializer
from app.Models.users_interests import User_Interest
from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework import status


class Oasis_Select_Interest_CRUD(viewsets.ModelViewSet):
    queryset = User_Interest.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserInterestSerializer
    
    
    
    def create(self, request, *args, **kwargs):
        # check if the user already has a record
        if User_Interest.objects.filter(user=request.user).exists():
            return Response({"error": "User already exists!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
   