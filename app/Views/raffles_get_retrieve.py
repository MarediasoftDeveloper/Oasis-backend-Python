from rest_framework.views import APIView
from rest_framework import generics
from venue.models.raffles import Raffles
from app.Models.raffles_entry import Raffles_Entry
from venue.Serializers.raffles_serializer import RafflesSerializer
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response

class RafflesGetView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class = RafflesSerializer

    def list(self, request, *args, **kwargs):
        queryset = Raffles.objects.filter(is_approved='approved')
        data=[]
        raffles_count = len(queryset)
        serialized=self.get_serializer(queryset)
        data = []
        for raffle in queryset:
            # Count how many times this raffle has been achieved
            participants = Raffles_Entry.objects.filter(raffle=raffle).count()

            # Serialize the raffle itself
            serialized_raffle = RafflesSerializer(raffle).data  # Serializing the raffle object

            # Add the achiever count to the serialized raffle data
            serialized_raffle["participants"] = participants
            data.append(serialized_raffle)

        # Return the response
        return Response({
            "raffles_count": raffles_count,
            "raffles": data  # Use 'data' instead of serialized.data here
        })




class RafflesRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Raffles.objects.all()
    serializer_class = RafflesSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get the raffle instance
        raffle = self.get_object()

        # Count how many times this raffle has been achieved
        raffle_achieve_count = Raffles_Entry.objects.filter(raffle=raffle).count()

        # Serialize the raffle
        serialized_raffle = self.get_serializer(raffle).data

        # Add the achieved count to the serialized raffle
        serialized_raffle["participants"] = raffle_achieve_count

        # Return the response with the serialized data and achieved count
        return Response(serialized_raffle)