from rest_framework import serializers
from app.Models.stamps import Stamps
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.utils import timezone



class StampSerializer(serializers.ModelSerializer):
    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)
    class Meta:
        model = Stamps
        fields = '__all__'

    def validate(self, data):
        request = self.context["request"]
        today = timezone.localdate()

        stamp_exists = Stamps.objects.filter(
            user=request.user,
            stamped_at__date=today
        ).exists()

        if stamp_exists:
            raise serializers.ValidationError({
                "error": "You have already stamped today."
            })

        
        if stamp_exists:
            raise serializers.ValidationError({"error":"You have already collected a stamp today."}) 
    
        return data

