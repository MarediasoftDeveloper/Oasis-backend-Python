from rest_framework import serializers
from app.Models.events import Events
from venue.models.badges import Badges
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.qr_info_serializer import VenueQRInfoSerializer
from django.utils import timezone
from venue.models.qr_info_model import QR_Info

class EventAppSerializer(serializers.ModelSerializer):
    created_by = Customer_Serializer(read_only=True)
    badge = BadgesSerializer(read_only=True)

    class Meta:
        model = Events
        fields='__all__'
        read_only_fields = ['created_by', 'badge']
    





class EventStaffSerializer(serializers.ModelSerializer):
    created_by = Customer_Serializer(read_only=True)
    badge = BadgesSerializer(read_only=True)
   
    # Allow writing by ID
    badge_id = serializers.PrimaryKeyRelatedField(
        queryset=Badges.objects.all(),
        source='badge',
        write_only=True,
        required=True
    )


    class Meta:
        model = Events
        fields = "__all__"
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    # -------------------------
    # FIELD VALIDATIONS
    # -------------------------

    def validate(self, attrs):
        start_date = attrs.get('event_start_date')
        close_date = attrs.get('event_close_date')
        badge = attrs.get('badge_id')

        if start_date and close_date:
            if close_date <= start_date:
                raise serializers.ValidationError(
                    {"error": "Event close date must be after start date."}
                )

        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')


        if (latitude and not longitude) or (longitude and not latitude):
            raise serializers.ValidationError({
               "error":"Both latitude and longitude must be provided together."
            })
        
        if Events.objects.filter(badge__id=badge).exists():
            raise serializers.ValidationError({"error":"Event associated with this badge is already exits."})   

        return attrs

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, validated_data):
        request = self.context.get('request')
        start_date = validated_data.get('event_start_date')
        close_date = validated_data.get('event_close_date')
        status = validated_data.get('status')

        # Automatically assign creator
        if request and hasattr(request, "user"):
            validated_data['created_by'] = request.user

        # Auto-set status based on date
        now = timezone.now()

        if start_date and close_date:
            if start_date > now:
                validated_data['status'] = 'upcoming'
            elif start_date <= now <= close_date:
                validated_data['status'] = 'live'
            elif close_date < now:
                validated_data['status'] = 'completed'    

        event = Events.objects.create(**validated_data)
        return event

    # -------------------------
    # UPDATE
    # -------------------------

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)


        # Recalculate status if dates changed
        start_date = instance.event_start_date
        close_date = instance.event_close_date
        status = validated_data.pop('status')
        now = timezone.now()

        if start_date and close_date:
            if start_date > now:
                instance.status = 'upcoming'
            elif start_date <= now <= close_date:
                instance.status = 'live'
            elif close_date < now:
                instance.status = 'completed'

        if status:
            instance.status=status

        instance.save()
        return instance