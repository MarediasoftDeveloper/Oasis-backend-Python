from rest_framework import viewsets
from app.Models.trails.trailModel import Trail 
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer 
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10        
    page_size_query_param = 'page_size'
    max_page_size = 50


class TrailCrud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
    pagination_class = StandardResultsSetPagination




