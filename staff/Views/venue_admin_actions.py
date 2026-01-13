from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.models.venue_info import Venue_Info
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.models import Customer
from staff.Permissions.admin_only_permission import Request_By_Admin_Only

class Venue_Info_Approve_Delete(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def patch(self, request, pk):
        venue = Venue_Info.objects.filter(venue__id=pk).first()

        if not venue:
            return Response(
                {"error": "Venue not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ALLOWED_STATUSES = ["approved", "suspended", "pending"]

        if new_status not in ALLOWED_STATUSES:
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        venue.status = new_status
        venue.save()

        return Response(
            {"message": f"Venue '{venue.venue_name}' successfully {new_status}!"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        venue = Venue_Info.objects.filter(venue__id=pk).first()

        if not venue:
            return Response(
                {"error": "Venue not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        venue.delete()

        return Response(
            {"message": "Venue successfully deleted"},
            status=status.HTTP_200_OK
        )
