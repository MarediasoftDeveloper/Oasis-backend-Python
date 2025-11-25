from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from venue.models.raffles import Raffles
from app.Models.earned_points import Earned_Points
from app.Models.raffles_entry import Raffles_Entry
from app.models import Customer_profile
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Serializers.raffles_entry_serializer import RafflesEntrySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from random import randint
from django.db.models import Max
from app.Views.functions.referrals_utils import add_points_to_user

class Withdraw_of_Raffle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raffle_id = request.data.get('raffle_id')

        if not raffle_id:
            return Response({"error": "Raffle ID is required!"},status=400)

        # Fetch all entries for the specific raffle
        get_raffle_entries = Raffles_Entry.objects.filter(raffle__id=raffle_id)
        get_entries = get_raffle_entries.filter(is_winner=False)


        if not get_entries.exists():
            return Response({"error": "No entries found for the specified raffle!"}, status=400)
       
        if not get_entries.first().raffle.venue ==request.user:
            return Response({"error": "You are not allowed to withdraw this raffle!"},status=400)


        # Get the randomly selected entry
        get_winner_entry = get_entries.order_by('?').first()
       
        if get_raffle_entries.filter(is_winner=True).count() >= get_winner_entry.raffle.num_of_winners:
            return Response({"error": "This Raffle has reached its number of winners!"}, status=400)

        # Check if the raffle has already reached its winner limit

        # Try to get the winner's customer profile
        try:
            get_winner = Customer_profile.objects.get(customer=get_winner_entry.user)
        except Customer_profile.DoesNotExist:
            return Response({"error": "Customer profile not found for the winner."}, status=400)

        # Reward points if applicable
        if get_winner_entry.raffle.rewarded_points:
            Earned_Points.objects.create(customer=get_winner_entry.user, points_earned=get_winner_entry.raffle.rewarded_points)
            get_winner.total_redeemed_points += get_winner_entry.raffle.rewarded_points
            get_winner.save()

        # Mark the entry as the winner
        get_winner_entry.is_winner = True
        get_winner_entry.save()

        # Serialize the winner's profile and return as a response
        serialized = CustomerProfileSerializer(get_winner)
     
      
        return Response({"winner": serialized.data,
                        "reward": get_winner_entry.raffle.rewards
                         })






            


    