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
        now = timezone.now()
        current_day = now.day
        current_month = now.month
        current_year = now.year
        request = self.context.get('request')
        # Check if a stamp already exists for today for this user
        stamp_exists = Stamps.objects.filter(
            user=request.user,
            stamped_at__day=current_day,
            stamped_at__month=current_month,
            stamped_at__year=current_year
        ).exists()

        
        if stamp_exists:
            raise serializers.ValidationError({"error":"You have already collected a stamp today."}) 
    
        return data

