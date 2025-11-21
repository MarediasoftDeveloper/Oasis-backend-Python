from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from app.Models.raffles_entry import Raffles_Entry
from app.models import Customer_profile
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.db.models import Prefetch


class Raffles_Participant_List(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # Prefetch the customer profiles to avoid N+1 query problem
        raffle_entries = Raffles_Entry.objects.filter(raffle=id, raffle__is_approved='approved').select_related('user').prefetch_related(
            Prefetch('user__customer_profile', queryset=Customer_profile.objects.all(), to_attr='user_profile')
        )


        # Prepare data
        data = []
        for entry in raffle_entries:
            profile = entry.user.customer_profile if entry.user.customer_profile else None  # Access the related profile directly
            if profile:
                serialized_profile = CustomerProfileSerializer(profile).data
                data.append(serialized_profile)

        if not data:
            return Response({"error": "No participants found for this raffle."}, status=404)

        return Response({"data": data})
    


