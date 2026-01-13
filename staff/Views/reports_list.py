from rest_framework import generics
from app.Models.reporting_and_complains import ReportingAndComplains
from app.Models.posts import Post
from app.Serializers.reportAndcomplainSerializer import ReportAndComplainListSerializer, ReportAndComplainSerializer
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10         
    page_size_query_param = 'page_size'
    max_page_size = 50

class ReportsList(generics.ListAPIView):
    permission_classes=[IsAuthenticated, Request_By_Admin_Only]
    queryset = ReportingAndComplains.objects.all()
    serializer_class=ReportAndComplainListSerializer
    pagination_class = StandardResultsSetPagination


class ReportsCreate(generics.CreateAPIView):
    permission_classes=[IsAuthenticated, Request_By_Admin_Only]
    queryset = ReportingAndComplains.objects.all()
    serializer_class=ReportingAndComplains


class ReportsRUD(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated, Request_By_Admin_Only]
    queryset = ReportingAndComplains.objects.all()
    serializer_class=ReportingAndComplains
    