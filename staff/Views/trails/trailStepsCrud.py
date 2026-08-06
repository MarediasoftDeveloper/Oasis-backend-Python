from rest_framework import viewsets
from app.Models.trails.trailSteps import TrailStep
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializerStaff
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10        
    page_size_query_param = 'page_size'
    max_page_size = 50



class TrailStepsCrud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = TrailStep.objects.all()
    serializer_class = TrailStepSerializerStaff
    pagination_class = StandardResultsSetPagination





