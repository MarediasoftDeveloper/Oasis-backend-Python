from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from app.Models.event_posts import EventPosts
from app.models import Customer
from app.Models.events import Events
from venue.models.venue_info import Venue_Info
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Serializers.post_serializer import PostSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from .events_serializer import EventAppSerializer
from app.Models.venues_participating_in_event import VenuesParticipatingEvents


class EventAppVenuesParticipatingSerializer(serializers.ModelSerializer):
    venues = VenueInfoSerializer(source='venues.venue_profile', read_only=True)

    venue_ids = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(user_role='2'),
        source='venues',
        write_only=True,
        required=True
    )

    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Events.objects.all(),
        source='event',
        write_only=True,
        required=True
    )

    

    class Meta:
        model = VenuesParticipatingEvents
        fields = [
            'id',
            'venues',
            'venue_ids',
            'event_id',
            'scans_to_achieve_next_tier',
            'available_from',
            'available_till'
            # add other model fields here if they exist
        ]

    
    def validate(self, attrs):
        venue = attrs.get('venues')
        event = attrs.get('event')
        request = self.context.get('request')

        if request and request.method=='POST' and VenuesParticipatingEvents.objects.filter(venues=venue, event=event).exists():
            raise serializers.ValidationError({
                "error": "This venue is already added to the participating venues list of this event."
            })

        # 1️⃣ Check event exists
        if not event:
            raise serializers.ValidationError({
                "error": "Event is required."
            })
        
        return attrs



class EventBulkVenuesParticipatingSerializer(serializers.ModelSerializer):
    venues = VenueInfoSerializer(source='venues.venue_profile', read_only=True)

    venue_ids = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(user_role='2'),
        many=True,
        write_only=True,
        required=True
    )

    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Events.objects.all(),
        source='event',
        write_only=True,
        required=True
    )

    class Meta:
        model = VenuesParticipatingEvents
        fields = [
            'id',
            'venues',
            'venue_ids',
            'event_id',
            'scans_to_achieve_next_tier',
            'available_from',
            'available_till'
        ]

    def validate(self, attrs):
        venue_ids = attrs.get('venue_ids', [])
        event = attrs.get('event')

        duplicates = VenuesParticipatingEvents.objects.filter(
            venues__in=venue_ids,
            event=event
        ).values_list('venues', flat=True)

        if duplicates:
            raise serializers.ValidationError({
                "error": f"Some venues are already participating in this event"
            })

        return attrs


    def create(self, validated_data):
        venue_ids = validated_data.pop('venue_ids')
        event = validated_data.pop('event')

        created_objects = []

        for venue in venue_ids:
            obj = VenuesParticipatingEvents.objects.create(
                venues=venue,
                event=event,
                **validated_data
            )
            created_objects.append(obj)

        return created_objects