from rest_framework.views import APIView
from app.Models.trails.trailModel import Trail 
from app.Models.trails.trailStepsRecord import TrailStepRecord
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer 
from app.Serializers.trailSerializers.trailsteprecord_serializer import TrailStepRecordSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response




class TrailStepsRecordStaffRetrieve(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]


    def get(self, request, trail_record_id):
        try:
            trail_steps_records = TrailStepRecord.objects.filter(trail_record_id=trail_record_id)
            serializer = TrailStepRecordSerializer(trail_steps_records, many=True)
            return Response(serializer.data)
        except TrailStepRecord.DoesNotExist:
            return Response({"error": "Trail steps records not found."}, status=404)
   