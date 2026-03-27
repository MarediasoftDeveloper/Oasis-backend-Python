from rest_framework.permissions import IsAuthenticated, AllowAny
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from venue.models.badges import BadgesLevel
from rest_framework.response import Response
from rest_framework import filters
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only
from rest_framework import viewsets 
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12         
    page_size_query_param = 'page_size'
    max_page_size = 50

class Badges_Levels_Crud_Staff(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_And_Organiser_Only]
    pagination_class = StandardResultsSetPagination
    queryset = BadgesLevel.objects.all().order_by('-id')
    filter_backends=[filters.SearchFilter]
    serializer_class=BadgesLevelSerializer
    search_fields = ['badge__name', 'category__category','points_per_task', 'category__num_of_task_to_achieve_badge']

    