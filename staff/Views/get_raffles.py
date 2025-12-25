from rest_framework.views import APIView
from rest_framework import generics
from venue.models.raffles import Raffles
from app.Models.raffles_entry import Raffles_Entry
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from venue.Serializers.raffles_serializer import RafflesStaffSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.response import Response
from django.db.models import Count, Sum

class GetRafflesForAdmin(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = RafflesStaffSerializer

    def list(self, request, *args, **kwargs):
        queryset = Raffles.objects.all().order_by('-id')
        data=[]

        serialized=self.get_serializer(queryset)
        entries = Raffles_Entry.objects.filter(raffle__in=queryset)
        tickets_sold = entries.filter(is_winner=True).values('raffle').annotate(sold=Count('*'))
        total_sold = tickets_sold.aggregate(total=Sum('sold'))['total']
        points_collected=entries.aggregate(total=Sum('raffle__points_to_join'))['total']
        
        data = []
        for raffle in queryset:
            # Count how many times this raffle has been achieved
            participants = Raffles_Entry.objects.filter(raffle=raffle)

            # Serialize the raffle itself
            serialized_raffle = RafflesStaffSerializer(raffle).data  # Serializing the raffle object

            # Add the achiever count to the serialized raffle data
            serialized_raffle["participants"] = participants.count()
            serialized_raffle["entries"] = RafflesEntrySerializer(participants, many=True).data
            data.append(serialized_raffle)

        # Return the response
        return Response({
            "raffles_count": queryset.count(),
            "total_sold":total_sold,
            "total_entries":entries.count(),
            "points_collected":points_collected,
            "raffles": data,
        })