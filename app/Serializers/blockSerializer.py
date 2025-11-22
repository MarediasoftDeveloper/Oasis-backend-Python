from rest_framework import serializers
from app.Models.users_blocking import UserBlocking
from app.Serializers.customer_signup_serializer import Customer_Serializer
from django.contrib.auth import get_user_model

User = get_user_model()

class BlockSerializer(serializers.ModelSerializer):
    blockedBy = Customer_Serializer(read_only=True)

    blockedUser = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),   # FIXED
        required=True
    )

    
    class Meta:
        model = UserBlocking
        fields = '__all__'
        read_only_fields = ['blockedBy']

    def validate(self, attrs):
        request = self.context['request']

        # Prevent blocking yourself
        if attrs['blockedUser'] == request.user:
            raise serializers.ValidationError({"error":"You cannot block yourself."})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['blockedBy'] = request.user
        return super().create(validated_data)