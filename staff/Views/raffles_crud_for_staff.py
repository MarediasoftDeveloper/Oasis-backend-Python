from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.raffles import Raffles
from app.Models.raffles_entry import Raffles_Entry
from venue.Serializers.raffles_serializer import RafflesSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from rest_framework.response import Response

class Raffles_Crud_for_Staff(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = RafflesSerializer

    def get_queryset(self):
        return Raffles.objects.all()


    

