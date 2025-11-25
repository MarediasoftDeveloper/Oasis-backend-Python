from rest_framework import serializers
from app.Models.DeviceFcmToken import DeviceFCM



class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFCM
        fields = ['fcm_token']
