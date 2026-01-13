from rest_framework.views import APIView
from rest_framework import generics
from app.Models.friendships import Friendships
from app.models import Customer, Customer_profile
from app.Serializers.customer_profile_serializer import CustomerProfileSerializerStaff
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, When, Case, F

class GetUserFriendsList(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def get(self, request, pk):
        customer = Customer.objects.filter(id=pk).first()
        friend_ids = Friendships.objects.filter(
            Q(request_sender=customer) | Q(request_getter=customer)
        ).annotate(
            friend_id=Case(
                When(request_sender=customer, then=F('request_getter')),
                When(request_getter=customer, then=F('request_sender')),
            )
        ).values_list('friend_id', flat=True)
        

   
        friends_data = Customer_profile.objects.filter(customer__id__in=friend_ids)
        friends = CustomerProfileSerializerStaff(friends_data, many=True)
   
        
        

        return Response({"friendships":friends.data})
        
        
      