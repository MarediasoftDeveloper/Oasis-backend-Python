from rest_framework import serializers
from app.Models.event_attendees import EventAttendees
from app.Models.events import Events
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.Serializers.badges_serializer import BadgesSerializer
from .events_serializer import EventAppSerializer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer


class EventAppAttendeesSerializer(serializers.ModelSerializer):
    # event = EventAppSerializer(read_only=True)
    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)
    event = serializers.PrimaryKeyRelatedField(
            queryset=Events.objects.all(),
            write_only=True
    )

    class Meta:
        model = EventAttendees
        fields = '__all__'
      

    def validate(self, attrs):
        request = self.context.get('request')
        event = attrs.get('event')

        # 1️⃣ Check event exists
        if not event:
            raise serializers.ValidationError({
                "error": "Event is required."
            })

        # 2️⃣ Validate post data exists
        if EventAttendees.objects.filter(user=request.user, event=event).exists():
            raise serializers.ValidationError({"error": "You have already joined this event!"})
        
        return attrs

    def create(self, validated_data):
        event = validated_data.pop('event')
        request = self.context.get('request')
        
        eventAttended = EventAttendees.objects.create(user=request.user,event=event, **validated_data)
        
        return eventAttended