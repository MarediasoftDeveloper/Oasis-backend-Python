from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from app.models import Customer_profile
from app.Models.posts import Post

class Customer_Feed(APIView):   

    permission_classes=[IsAuthenticated]

    def get(self, request):
        
        user = request.user
        public_profiles_ids = Customer_profile.objects.filter(customer=user, is_private=False).values_list('customer', flat=True)
        customer_posts = Post.objects.filter(user__id__in=public_profiles_ids)
        venue_posts = Post.objects.filter(user__user_role='2')

        print(customer_posts)
        print(venue_posts)

        return Response({"ids":list(public_profiles_ids)})
