from rest_framework import serializers
from app.Models.stamps import Stamps
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer

class StampSerializer(serializers.ModelSerializer):
    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)
    class Meta:
        model = Stamps
        fields = '__all__'
