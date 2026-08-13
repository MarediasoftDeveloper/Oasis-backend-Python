from rest_framework import viewsets
from app.Models.trails.trailModel import Trail 
from app.Models.trails.trailRecord import TrailRecord 
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer 
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializerStaff 
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

#verseion
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10        
    page_size_query_param = 'page_size'
    max_page_size = 50


class TrailCrud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
    pagination_class = StandardResultsSetPagination

    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True
            )

            response = self.get_paginated_response(
                serializer.data
            )


            response.data.update({
                "trails_count": queryset.count() or 0,
                "inactive_trails_count": queryset.exclude(is_active=True).count() or 0,
                "active_trails_count": queryset.filter(is_active=True).count() or 0,
                "total_trails_abandoned": TrailRecord.objects.filter(status=TrailRecord.Status.ABANDONED).count() or 0,
                "total_trails_attempted": TrailRecord.objects.all().count() or 0,
            })

            return response
        
        serializer = self.get_serializer(
            queryset,
            many=True
        )

        return Response({
            "trails_count": queryset.count() or 0,
            "inactive_trails_count": queryset.exclude(is_active=True).count() or 0,
            "active_trails_count": queryset.filter(is_active=True).count() or 0,
            "total_trails_abandoned": TrailRecord.objects.filter(status=TrailRecord.Status.ABANDONED).count() or 0,
            "total_trails_attempted": TrailRecord.objects.all().count() or 0,
            "trails": serializer.data
        })

  




    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serialized_data = serializer.data
        serialized_data["steps"] = TrailStepSerializerStaff(
            instance.steps.all(),
            many=True,
        ).data
        return Response(serialized_data)

  
