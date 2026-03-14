from rest_framework import serializers
from venue.models.challenges import Challenges
from app.models import Customer
from venue.models.qr_info_model import QR_Info
from venue.Serializers.qr_info_serializer import QRInfoSerializer, VenueQRInfoSerializer
from venue.Serializers.venue_badges_serializer import VenueBadgesSerializer
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import Badges
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from django.db.models import Count

class ChallengesSerializer(serializers.ModelSerializer):
    qr_code = QRInfoSerializer(read_only=True)
    venue = VenueInfoSerializer(source="venue.venue_profile", read_only=True)
    badge = VenueBadgesSerializer(read_only=True)
    venue_badge = serializers.PrimaryKeyRelatedField(
        queryset=Venue_Badges.objects.all(),
        required=True,
        write_only=True
    )
    class Meta:
        model = Challenges
        fields = '__all__'
        read_only_fields=['venue', 'qr_code', 'badge']
    
    def validate_description(self, value):
        """Ensure ending date is after starting date and badge is valid."""
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                {"error": "Description is too long."}
            )
        return value

    def validate(self, data):
        """Ensure ending date is after starting date and badge is valid."""

        starting_date = data.get('starting_date')
        ending_date = data.get('ending_date')
        venue_badge = data.get('venue_badge')

        # Validate date logic
        if starting_date and ending_date and ending_date < starting_date:
            raise serializers.ValidationError(
                {"error": "Ending date cannot be before the starting date."}
            )

        # Validate badge_id existence
        if not venue_badge:
            raise serializers.ValidationError({"error": "Badge ID is required."})

        # Validate active challenge for this badge already exists
        venue = self.context.get('request').user
        if not Venue_Badges.objects.filter(venue=venue, badge=venue_badge.badge).exists():
            raise serializers.ValidationError(
                {"error": "Currently you don't have selected this badge, Please select it first to create challenge on it!"}
            )
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Challenges.objects.filter(
                venue=venue,
                badge=venue_badge,
                is_ended=False
            ).exists():
                raise serializers.ValidationError(
                    {"error": "You already have an active challenge for this badge!"}
                )

        return data

    def validate_daily_times(self, value, field_name):
        """Ensure daily_open_time and daily_close_time are within valid range."""
        if value:
            if value.hour < 0 or value.hour >= 24 or value.minute < 0 or value.minute >= 60:
                raise serializers.ValidationError(f"{field_name} must be a valid time (HH:MM format).")
        return value

    def validate_open_time(self, value):
        """Validate that daily open time is a valid time."""
        return self.validate_daily_times(value, "daily_open_time")

    def validate_close_time(self, value):
        """Validate that daily close time is a valid time."""
        return self.validate_daily_times(value, "daily_close_time")


    def create(self, validated_data):
        """Create a new Challenge."""
        ending_at = validated_data.get('ending_at')
        venue_badge = validated_data.get('venue_badge')
        venue = self.context.get('request').user
        qr_obj = QR_Info(expires_at=ending_at)
        
        qr_obj.save()

        challenge = Challenges.objects.create(
            venue=venue,
            badge=venue_badge,
            qr_code = qr_obj,
            **validated_data
        )
        if hasattr(challenge, 'badge') and challenge.badge:
            challenge.badge.is_active = True
            challenge.badge.save()
        
        return challenge

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        badge_status = validated_data.pop('venue_badge_status')
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
       

        if badge_status:
            instance.badge.is_active = badge_status
            instance.badge.save()

        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()




class VenueChallengesSerializer(serializers.ModelSerializer):
    qr_code = VenueQRInfoSerializer(read_only=True)
    venue = VenueInfoSerializer(source="venue.venue_profile", read_only=True)
    badge = VenueBadgesSerializer(read_only=True)
    venue_badge = serializers.PrimaryKeyRelatedField(
        queryset=Venue_Badges.objects.all(),
        required=True,
        write_only=True
    )
    class Meta:
        model = Challenges
        fields = '__all__'
        read_only_fields=['venue', 'qr_code', 'badge', 'is_approved']
    
    def validate_description(self, value):
        """Ensure ending date is after starting date and badge is valid."""
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                {"error": "Description is too long."}
            )
        return value

    
    def validate(self, data):
        """Ensure ending date is after starting date and badge is valid."""

        starting_date = data.get('starting_date')
        ending_date = data.get('ending_date')
        venue_badge = data.get('venue_badge')

        # Validate date logic
        if starting_date and ending_date and ending_date < starting_date:
            raise serializers.ValidationError(
                {"error": "Ending date cannot be before the starting date."}
            )

        # Validate badge_id existence
        if not venue_badge:
            raise serializers.ValidationError({"error": "Badge ID is required."})

        # Validate active challenge for this badge already exists
        venue = self.context.get('request').user
        if not Venue_Badges.objects.filter(venue=venue, badge=venue_badge.badge).exists():
            raise serializers.ValidationError(
                {"error": "Currently you don't have selected this badge, Please select it first to create challenge on it!"}
            )
        request = self.context.get('request')
        if request and request.method =='POST':
            if Challenges.objects.filter(
                venue=venue,
                badge=venue_badge,
                is_ended=False
            ).exists():
                raise serializers.ValidationError(
                    {"error": "You already have an active challenge for this badge!"}
                )

        return data

    def validate_daily_times(self, value, field_name):
        """Ensure daily_open_time and daily_close_time are within valid range."""
        if value:
            if value.hour < 0 or value.hour >= 24 or value.minute < 0 or value.minute >= 60:
                raise serializers.ValidationError(f"{field_name} must be a valid time (HH:MM format).")
        return value

    def validate_open_time(self, value):
        """Validate that daily open time is a valid time."""
        return self.validate_daily_times(value, "daily_open_time")

    def validate_close_time(self, value):
        """Validate that daily close time is a valid time."""
        return self.validate_daily_times(value, "daily_close_time")


    def create(self, validated_data):
        """Create a new Challenge."""
        ending_at = validated_data.get('ending_at')
        venue_badge = validated_data.pop('venue_badge')
        qr_obj = QR_Info(expires_at=ending_at)
        qr_obj.save()
        validated_data['badge'] = venue_badge
        challenge = Challenges.objects.create(
            qr_code = qr_obj,
            **validated_data
        )
        if hasattr(challenge, 'badge') and challenge.badge:
            challenge.badge.is_active = True
            challenge.badge.save()
        
        return challenge

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        is_ended = validated_data.get('is_ended')
        venue_badge = validated_data.pop('venue_badge', None)
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if venue_badge is not None:
            instance.badge = venue_badge

        

        if is_ended is not None:
            instance.badge.is_active = not is_ended
            instance.badge.save()


        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()




class StaffChallengesSerializer(serializers.ModelSerializer):
    qr_code = VenueQRInfoSerializer(read_only=True)
    venue = VenueInfoSerializer(source="venue.venue_profile", read_only=True)
    venue_id=serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.filter(user_role='2'),
        required=True,
        write_only=True
    )
    badge = VenueBadgesSerializer(read_only=True)
    venue_badge = serializers.PrimaryKeyRelatedField(
        queryset=Badges.objects.all(),
        required=True,
        write_only=True
    )
    class Meta:
        model = Challenges
        fields = '__all__'
        read_only_fields=['venue', 'qr_code', 'badge']
    
    def validate_description(self, value):
        """Ensure ending date is after starting date and badge is valid."""
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                {"error": "Description is too long."}
            )
        return value

    
    def validate(self, data):
        """Ensure ending date is after starting date and badge is valid."""

        starting_date = data.get('starting_date')
        ending_date = data.get('ending_date')
        venue_badge = data.get('venue_badge')
        venue = data.get('venue_id')

        # Validate date logic
        if starting_date and ending_date and ending_date < starting_date:
            raise serializers.ValidationError(
                {"error": "Ending date cannot be before the starting date."}
            )

        # Validate badge_id existence
        if not venue_badge:
            raise serializers.ValidationError({"error": "Badge should be selected"})
       
        
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Challenges.objects.filter(
                venue=venue,
                badge__badge=venue_badge,
                is_ended=False
            ).exists():
                raise serializers.ValidationError(
                    {"error": "You already have an active challenge for this badge!"}
                )

        return data

    def validate_daily_times(self, value, field_name):
        """Ensure daily_open_time and daily_close_time are within valid range."""
        if value:
            if value.hour < 0 or value.hour >= 24 or value.minute < 0 or value.minute >= 60:
                raise serializers.ValidationError(f"{field_name} must be a valid time (HH:MM format).")
        return value

    def validate_open_time(self, value):
        """Validate that daily open time is a valid time."""
        return self.validate_daily_times(value, "daily_open_time")

    def validate_close_time(self, value):
        """Validate that daily close time is a valid time."""
        return self.validate_daily_times(value, "daily_close_time")

    def create(self, validated_data):
        """Create a new Challenge."""
        ending_at = validated_data.get('ending_at')
        venue_badge = validated_data.pop('venue_badge')
        venue = validated_data.pop('venue_id')
        qr_obj = QR_Info(expires_at=ending_at)
        
        qr_obj.save()
    
        if venue_badge:
            getVenueBadge, _ = Venue_Badges.objects.get_or_create(venue=venue, badge=venue_badge)
            
        challenge = Challenges.objects.create(
            venue=venue,
            badge=getVenueBadge,
            qr_code = qr_obj,
            **validated_data
        )
        
        if hasattr(challenge, 'badge') and challenge.badge:
            challenge.badge.is_active = True
            challenge.badge.save()
        
        return challenge

    def update(self, instance, validated_data):
        """Update an existing Challenge."""
        is_ended = validated_data.get('is_ended')
        venue_badge = validated_data.pop('venue_badge')
        venue = validated_data.pop('venue_id')
        
    

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if venue_badge:
            getVenueBadge,_ =Venue_Badges.objects.get_or_create(venue=venue, badge=venue_badge)
            instance.badge=getVenueBadge
        if venue:
            instance.venue=venue
            
        if is_ended is not None:
            instance.badge.is_active = not is_ended
            instance.badge.save()

        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()



   






    