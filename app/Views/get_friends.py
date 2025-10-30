from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Serializers.friendship_serializer import FriendshipSerializer
from app.Models.friendships import Friendships
from app.models import Customer_profile
from app.Models.earned_badges_by_user import Earned_Badges
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q




class Get_Friends(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendshipSerializer
    
    def get(self, request):
        data=[]
        friends = Friendships.objects.filter(
            Q(request_sender=request.user, status='accepted') |
            Q(request_getter=request.user, status='accepted')
        )

        for friend in friends:
            if friend.request_sender == request.user:
                get_profile = Customer_profile.objects.get(customer=friend.request_getter)
                earned_badges = Earned_Badges.objects.filter(user=friend.request_getter).count()
                serialized_profile = CustomerProfileSerializer(get_profile)
                data.append({
                    'profile':{**serialized_profile.data},
                    'earned_badges': earned_badges
                })
            else:
                get_profile = Customer_profile.objects.get(customer=friend.request_sender)
                earned_badges = Earned_Badges.objects.filter(user=friend.request_sender).count()
                serialized_profile = CustomerProfileSerializer(get_profile)
                data.append({
                    'profile':{**serialized_profile.data},
                    'earned_badges': earned_badges
                })
        if not data:
            return Response({"error": "No friends to show!"}, status=404)
        
        return Response(data)

   
