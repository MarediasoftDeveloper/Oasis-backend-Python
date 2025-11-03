from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework import status
from app.models import Customer_profile
from app.Serializers.post_serializer import PostSerializer
from app.Models.posts import Post
from rest_framework.pagination import PageNumberPagination
from itertools import chain

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10                     # ✅ Return 10 posts by default
    page_size_query_param = 'page_size'
    max_page_size = 50

class Customer_Feed(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def get(self, request):
        paginator = StandardResultsSetPagination()

        public_profiles_ids = Customer_profile.objects.filter(is_private=False).values_list('customer', flat=True)
        customer_posts = Post.objects.filter(user__id__in=public_profiles_ids)
        venue_posts = Post.objects.filter(user__user_role='2')

        posts = customer_posts.union(venue_posts).order_by('-id')  #  Optimized

        # Apply pagination
        paginated_posts = paginator.paginate_queryset(posts, request)
        serialized_posts = PostSerializer(paginated_posts, many=True)

        return paginator.get_paginated_response(serialized_posts.data)




class Customer_Feed_Retrieve(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field='slug'

        
        