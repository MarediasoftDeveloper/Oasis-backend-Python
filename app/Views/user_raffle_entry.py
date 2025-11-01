from rest_framework.views import APIView
from rest_framework import generics
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.raffles_entry import Raffles_Entry

class User_Raffles_Entry(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Raffles_Entry.objects.all()
    serializer_class = RafflesEntrySerializer   

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




