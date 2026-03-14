from rest_framework import serializers
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from app.Models.event_badges_earned import EventBadgesEarned
from app.Models.earned_badges_by_user import Earned_Badges
from app.Models.events import Events
from venue.models.venue_badges import Venue_Badges
from rest_framework.response import Response
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from .events_serializer import EventAppSerializer
from app.Views.functions.get_level_of_user_badge import get_level_points_per_task_for_events
from venue.models.badge_category import Badge_Category
import calendar



def is_time_in_range(start, end, now):
    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end

class EventBadgeEarnedSerializer(serializers.ModelSerializer):

    code = serializers.CharField(write_only=True, required=True)
    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)
    event = EventAppSerializer(read_only=True)
    
    class Meta:
        model = EventBadgesEarned
        fields = '__all__'
        read_only_fields = ['earned_at', 'user', 'event']  # automatically handled

    def validate(self, data):
        """Validate cooldown time and daily cap before allowing scan."""
        request = self.context.get('request')
        code = data.get('code')
        event = Events.objects.filter(qr_code__code=code).first()

        
        if not event:
            raise serializers.ValidationError({"error":"Invalid QR Code"})
        
        user = request.user
        
     

        now = timezone.now()  # Use timezone aware current time
    
        # --- Check if Challenge hasn't started yet ---
        if now < event.event_start_date:
            raise serializers.ValidationError({
                "error": f"This Event will start on {event.event_start_date}."
            })
        
        statuses = ['upcoming', 'draft', 'completed']
        if event.status in statuses:
            raise serializers.ValidationError({
                "error": f"Sorry! This Event is not available right now"
            })

        if event.event_close_date < now:
            event.status == 'completed'
            raise serializers.ValidationError({
                "error": f"This Event ended on {event.event_close_date}."
            })
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        code = validated_data.pop('code')
        try:
            event = Events.objects.filter(qr_code__code__iexact=code).first()
        except Events.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid QR code!"})


        actual_badge = event.badge
        points = get_level_points_per_task_for_events(user, event, actual_badge)
        validated_data['user'] = user
        validated_data['event'] = event
        validated_data['points_issued'] = points
        achievement = EventBadgesEarned.objects.create(user=user, event=event, points_issued=points)
        
        return achievement

    def update(self, instance, validated_data):
        """Update an existing Challenge_Achiever record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()


class GetEventBadgeEarnedSerializer(serializers.ModelSerializer):

    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)
    event = EventAppSerializer(read_only=True)
    
    class Meta:
        model = EventBadgesEarned
        fields = '__all__'
        read_only_fields = ['earned_at', 'user', 'event']  # automatically handled

