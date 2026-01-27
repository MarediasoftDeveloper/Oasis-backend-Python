from app.Serializers.stamps_serializer import StampSerializer
from app.Models.stamps import Stamps
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.models import Customer
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from django.db.models import Sum


class UserStamps(APIView):

    permission_classes = [IsAuthenticated, Request_By_Admin_Only]  # add admin-only if required

    def get(self, request, pk):
        stamps = Stamps.objects.filter(user__id=pk).order_by('-stamped_at')
        serialized = StampSerializer(stamps, many=True)
        total_points_by_stamps = int(stamps.count()) * 30
        return Response({"stamps": serialized.data, "total_stamps_collected":stamps.count(), "total_stamp_points": total_points_by_stamps})


