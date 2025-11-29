from rest_framework.views import APIView
from rest_framework import generics, filters
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
    page_size = 15                 
    page_size_query_param = 'page_size'
    max_page_size = 50



class Customer_List(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class=CustomerProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['customer__username', 'customer__email']
    queryset = Customer_profile.objects.all()    
    pagination_class = StandardResultsSetPagination



    def get_queryset(self):
        public_profiles = super().get_queryset()    
        user = self.request.user
        blocked_relations = UserBlocking.objects.filter(Q(blockedBy=user)|Q(blockedUser=user))
        if blocked_relations.exists():
            blocked_ids = set(blocked_relations.values_list("blockedBy_id", flat=True)) | \
                set(blocked_relations.values_list("blockedUser_id", flat=True))
            public_profiles = public_profiles.exclude(customer__id__in=blocked_ids)
        
        # friend_relations = Friendships.objects.filter(Q(request_sender=user)|Q(request_getter=user))
        # if friend_relations.exists():
        #     friends_ids = set(friend_relations.values_list("request_sender__id", flat=True)) | \
        #         set(friend_relations.values_list("request_getter__id", flat=True))
        #     public_profiles = public_profiles.exclude(customer__id__in=friends_ids)

        public_profiles = public_profiles.exclude(customer=user)
            
        return public_profiles
    

   
        
        
        
    
        
        


        
            

      