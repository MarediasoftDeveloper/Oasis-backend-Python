from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework import status
from app.models import Customer_profile
from app.Models.posts import Post
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Models.users_blocking import UserBlocking
from app.Models.friendships import Friendships
from rest_framework.pagination import PageNumberPagination
from itertools import chain
from django.db.models import Q


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20                     # ✅ Return 10 posts by default
    page_size_query_param = 'page_size'
    max_page_size = 50

class Customer_List(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def get(self, request):
        paginator = StandardResultsSetPagination()

        public_profiles = Customer_profile.objects.all()
        
        
        blocked_relations = UserBlocking.objects.filter(Q(blockedBy=self.request.user)|Q(blockedUser=self.request.user))

        friend_relations = Friendships.objects.filter(Q(request_sender=self.request.user)|Q(request_getter=self.request.user))

        blocked_ids = set(blocked_relations.values_list("blockedBy_id", flat=True)) | \
            set(blocked_relations.values_list("blockedUser_id", flat=True))
        
        friends_ids = set(friend_relations.values_list("request_sender__id", flat=True)) | \
            set(friend_relations.values_list("request_getter__id", flat=True))
        

        if blocked_relations.exists():
            public_profiles = public_profiles.exclude(customer__id__in=blocked_ids)
            
        if friend_relations.exists():
            public_profiles = public_profiles.exclude(customer__id__in=friends_ids)
        
        
        public_profiles = public_profiles.exclude(customer__id=self.request.user.id)
            

            
        # Apply pagination
        paginated_profiles = paginator.paginate_queryset(public_profiles, request)
        serialized_profiles = CustomerProfileSerializer(paginated_profiles, many=True)

        return paginator.get_paginated_response(serialized_profiles.data)