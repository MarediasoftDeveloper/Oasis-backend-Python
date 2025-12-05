from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.notifications import Notifications
from app.Serializers.notification_serializer import NotificationSerializer

class NotificationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class=NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notifications.objects.filter(user=user).order_by('-id')
    