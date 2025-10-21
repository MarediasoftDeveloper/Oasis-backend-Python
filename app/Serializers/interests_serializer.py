from rest_framework import serializers
from app.Models.interests import Customer_Interest


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_Interest
        fields = '__all__'
    