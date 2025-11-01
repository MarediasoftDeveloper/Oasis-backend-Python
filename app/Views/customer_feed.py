from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from app.models import Customer_profile
from app.Serializers.post_serializer import PostSerializer
from app.Models.posts import Post

class Customer_Feed(APIView):   

    permission_classes=[IsAuthenticated]

    def get(self, request):
        
        public_profiles_ids = Customer_profile.objects.filter(is_private=False).values_list('customer', flat=True)
        customer_posts = Post.objects.filter(user__id__in=public_profiles_ids)
        venue_posts = Post.objects.filter(user__user_role='2')
        serialized_customer_posts = PostSerializer(customer_posts, many=True)
        serialized_venue_posts = PostSerializer(venue_posts, many=True)
        
        return Response({"customer_posts":serialized_customer_posts.data, "venues_posts":serialized_venue_posts.data})
