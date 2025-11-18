from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Permissions.write_by_customer_only import WriteByCustomerOnly
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.posts import Post 
from app.Serializers.post_serializer import PostSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class Post_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByCustomerOnly]
    serializer_class = PostSerializer
    lookup_field ='slug'
    
    def get_queryset(self): 
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)