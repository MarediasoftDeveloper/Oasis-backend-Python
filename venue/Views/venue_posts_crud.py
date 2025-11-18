from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.posts import Post 
from app.Serializers.post_serializer import PostSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class Venue_Post_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    serializer_class = PostSerializer
    lookup_field ='slug'
    
    def get_queryset(self): 
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class VenuePosts(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, venue_id):
        posts = Post.objects.filter(user__id=venue_id)
        serilizer = PostSerializer(posts, many=True)
        return Response({"posts":serilizer.data})
