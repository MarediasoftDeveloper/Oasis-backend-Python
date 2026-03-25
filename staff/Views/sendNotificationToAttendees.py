# Create your views here.
from rest_framework.views import APIView
from rest_framework import status, generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from app.Views.utils.fcm import send_push_notification
from app.Models.event_attendees import EventAttendees
from app.models import Customer


class SendNotificationToAttendees(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def post(self, request):
        event = request.data.get('event_id')
        title = request.data.get('title')
        description = request.data.get('description')
        
        ids = EventAttendees.objects.filter(event__id=event).values_list('user_id', flat=True)
        customers  = list(Customer.objects.filter(id__in=ids))

        result = send_push_notification(
            customers,
            title,
            description
        )

        return Response({"message":"Notificaiton have been sent successfully"})