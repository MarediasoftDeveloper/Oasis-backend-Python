from rest_framework.views import APIView
from rest_framework import generics
from venue.models.raffles import Raffles
from venue.Serializers.raffles_serializer import RafflesSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only

class RafflesGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Raffles.objects.all()
    serializer_class = RafflesSerializer




class RafflesRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Raffles.objects.all()
    serializer_class = RafflesSerializer