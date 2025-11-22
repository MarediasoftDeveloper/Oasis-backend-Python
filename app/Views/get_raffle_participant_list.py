from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from app.Models.raffles_entry import Raffles_Entry
from app.models import Customer_profile
from app.Models.users_blocking import UserBlocking
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.db.models import Prefetch
from django.db.models import Q

class Raffles_Participant_List(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # Prefetch the customer profiles to avoid N+1 query problem
        raffle_entries = Raffles_Entry.objects.filter(raffle=id, raffle__is_approved='approved')

        blocked_relations = UserBlocking.objects.filter(Q(blockedBy=self.request.user)|Q(blockedUser=self.request.user))
        blocked_ids = set(blocked_relations.values_list("blockedBy_id", flat=True)) | \
            set(blocked_relations.values_list("blockedUser_id", flat=True))

        if blocked_relations.exists():
            blocked_ids.discard(self.request.user.id)
            raffle_entries = raffle_entries.exclude(user__id__in=blocked_ids)
        
        
        raffle_entries = raffle_entries.select_related('user').prefetch_related(
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
    


