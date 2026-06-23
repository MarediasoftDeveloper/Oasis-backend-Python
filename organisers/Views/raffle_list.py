from datetime import datetime

from rest_framework import generics 
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from venue.models.raffles import Raffles
from organisers.serializers.raffle_list_serializer import RaffleListSerializer



class RaffleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Raffles.objects.all()
    serializer_class = RaffleListSerializer