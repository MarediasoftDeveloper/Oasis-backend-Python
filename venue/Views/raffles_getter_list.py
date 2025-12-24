from rest_framework.views import APIView
from rest_framework import generics
from venue.models.raffles import Raffles
from app.Models.raffles_entry import Raffles_Entry
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from venue.Serializers.raffles_serializer import RafflesSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from rest_framework.response import Response
from django.db.models import Count, Sum

class MyRafflesGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = RafflesSerializer

    def list(self, request, *args, **kwargs):
        queryset = Raffles.objects.filter(venue=request.user).order_by('-created_at')
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
            serialized_raffle = RafflesSerializer(raffle).data  # Serializing the raffle object

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




class MyRafflesRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = RafflesSerializer

    def get_queryset(self):
        return Raffles.objects.filter(venue=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # Get the raffle instance
        raffle = self.get_object()

        # Count how many times this raffle has been achieved
        raffle_achieve = Raffles_Entry.objects.filter(raffle=raffle)

        # Serialize the raffle
        serialized_raffle = self.get_serializer(raffle).data

        # Add the achieved count to the serialized raffle
        serialized_raffle["participants"] = raffle_achieve.count()
        serialized_raffle["winner"] = raffle_achieve.filter(is_winner=True).count()

        # Return the response with the serialized data and achieved count
        return Response(serialized_raffle)