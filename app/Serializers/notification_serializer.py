from rest_framework import serializers
from app.Models.notifications import Notifications


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        exclude =['user']