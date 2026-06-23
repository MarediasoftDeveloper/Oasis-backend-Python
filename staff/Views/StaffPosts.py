from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from app.Models.posts import Post 
from app.Serializers.post_serializer import PostSerializer, PostSerializerStaff
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only





class Post_Crud_Staff(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    serializer_class = PostSerializer
    lookup_field ='slug'
    
    def get_queryset(self): 
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_object(self):
        slug = self.kwargs.get(self.lookup_field)
        obj = Post.objects.get(slug=slug)

        # Only check object-level permissions for update/delete
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            self.check_object_permissions(self.request, obj)

        return obj
    








class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10         
    page_size_query_param = 'page_size'
    max_page_size = 50
    

class Admin_Post_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    pagination_class = StandardResultsSetPagination
    serializer_class = PostSerializerStaff
    lookup_field ='slug'
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
        
   