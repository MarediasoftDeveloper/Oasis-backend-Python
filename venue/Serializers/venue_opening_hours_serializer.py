from rest_framework import serializers
from venue.models.venue_opening_hours import Venue_Opening_Hours

class VenueOpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue_Opening_Hours
        fields = '__all__'

    def validate_venue(self, value):
        """
        Ensure that each venue can only have one set of opening hours.
        Allow update (don't block if instance already exists).
        """
        # When creating, prevent duplicates
        if self.instance is None and Venue_Opening_Hours.objects.filter(venue=value).exists():
            raise serializers.ValidationError("Opening hours for this venue already exist.")
        return value

    def validate(self, data):
        """
        Basic validation: all day fields should be non-empty.
        (You can later add time-format checks if needed.)
        """
        days = [
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday'
        ]

        for day in days:
            value = data.get(day)
            if not value or not str(value).strip():
                raise serializers.ValidationError({day: f"{day.capitalize()} hours cannot be empty."})
        return data

    def create(self, validated_data):
        """Create a new Venue_Opening_Hours instance."""
        instance = Venue_Opening_Hours.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        """Update an existing Venue_Opening_Hours instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion if you need custom logic."""
        instance.delete()
