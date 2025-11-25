from rest_framework import serializers
from app.Models.users_blocking import UserBlocking
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class BlockSerializer(serializers.ModelSerializer):
    blockedBy = Customer_Serializer(read_only=True)
    blockedUserId = serializers.PrimaryKeyRelatedField(
        source='blockedUser',
        queryset=User.objects.all(),
        write_only=True
    )

    # Read: system returns full profile
    blockedUser = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserBlocking
        fields = '__all__'
        read_only_fields = ['blockedBy', 'blockedUser']


    def get_blockedUser(self, instance):
        user = instance.blockedUser

        if user.user_role == '2':  # venue
            if hasattr(user, "venue_profile"):
                return VenueInfoSerializer(user.venue_profile).data 
            return {"error": "Venue profile missing"}

        # customer
        if hasattr(user, "customer_profile"):
            return CustomerProfileSerializer(user.customer_profile).data

        return {"id": user.id, "email": user.email, "profile": None}
    

    
    def validate(self, attrs):
        request = self.context['request']
        blocked_user = attrs['blockedUser']

        # Cannot block yourself
        if blocked_user == request.user:
            raise serializers.ValidationError({"error": "You cannot block yourself."})

        # Prevent duplicate blocking
        if UserBlocking.objects.filter(blockedBy=request.user, blockedUser=blocked_user).exists():
            raise serializers.ValidationError({"error": "This user is already blocked."})

        # Optional: Prevent venues/admins from blocking others
        if request.user.user_role in ['2', '3']:
            raise serializers.ValidationError({"error": "This account cannot block users."})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['blockedBy'] = request.user
        return super().create(validated_data)