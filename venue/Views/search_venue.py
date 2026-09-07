from rest_framework.views import APIView
from rest_framework import generics, filters
from venue.models.rewards import Rewards
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.models.venue_info import Venue_Info
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15               
    page_size_query_param = 'page_size'
    max_page_size = 50


class SearchVenueAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VenueInfoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['venue_name']
    queryset = Venue_Info.objects.filter(status='approved').order_by('-add_to_popular', 'venue_name')   
    pagination_class = StandardResultsSetPagination




