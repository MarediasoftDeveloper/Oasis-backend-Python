from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Serializers.interests_serializer import InterestSerializer
from app.Models.interests import Customer_Interest
from rest_framework import viewsets 



class Oasis_Interest_CRUD(viewsets.ModelViewSet):
    queryset = Customer_Interest.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = InterestSerializer