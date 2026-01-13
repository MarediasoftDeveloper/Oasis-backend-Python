from app.Views.utils.fcm import send_push_notification
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from app.models import Customer_profile, Customer
from rest_framework.response import Response


class SendNotificationToAllUsers(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
      
        customer = list(Customer.objects.filter(user_role='1'))
        result = send_push_notification(
            customer,
            title,
            description
        )
        print(result)
        return Response({"message":"Notificaiton have been sent successfully"})

