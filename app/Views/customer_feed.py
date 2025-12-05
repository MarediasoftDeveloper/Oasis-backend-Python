from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework import status
from app.models import Customer_profile
from app.Models.posts import Post
from app.Serializers.post_serializer import PostSerializer
from app.Models.users_blocking import UserBlocking
from rest_framework.pagination import PageNumberPagination
from itertools import chain
from django.db.models import Q
from app.Models.friendships import Friendships


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10                     # ✅ Return 10 posts by default
    page_size_query_param = 'page_size'
    max_page_size = 50

class Customer_Feed(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def get(self, request):
        paginator = StandardResultsSetPagination()
        user = request.user

        # ---- FRIEND LIST ----
        friend_rels = Friendships.objects.filter(
            Q(request_sender=user) | Q(request_getter=user),
            status="accepted"
        )

        friends_ids = set(friend_rels.values_list("request_sender_id", flat=True)) | \
                      set(friend_rels.values_list("request_getter_id", flat=True))
        friends_ids.discard(user.id)

        # ---- BLOCKED USERS ----
        blocked = UserBlocking.objects.filter(Q(blockedBy=user) | Q(blockedUser=user))
        blocked_ids = set(blocked.values_list("blockedBy_id", flat=True)) | \
                      set(blocked.values_list("blockedUser_id", flat=True))
        blocked_ids.discard(user.id)

        # ---- PUBLIC PROFILES ----
        public_ids = set(
            Customer_profile.objects.filter(is_private=False)
            .values_list("customer_id", flat=True)
        )

        # ---- PRIVATE PROFILES (ONLY FRIENDS allowed) ----
        private_ids = set(
            Customer_profile.objects.filter(is_private=True)
            .values_list("customer_id", flat=True)
        )

        allowed_private_ids = private_ids & friends_ids

        # Final allowed customers
        allowed_customer_ids = (public_ids | allowed_private_ids) - blocked_ids

        # ---- GET POSTS ----
        customer_posts = Post.objects.filter(user_id__in=allowed_customer_ids)
        venue_posts = Post.objects.filter(user__user_role="2").exclude(user_id__in=blocked_ids)

        posts = (customer_posts | venue_posts).order_by("-id")

        # ---- PAGINATION ----
        paginated = paginator.paginate_queryset(posts, request)
        serialized = PostSerializer(paginated, many=True)

        return paginator.get_paginated_response(serialized.data)




class Customer_Feed_Retrieve(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field='slug'

        
        