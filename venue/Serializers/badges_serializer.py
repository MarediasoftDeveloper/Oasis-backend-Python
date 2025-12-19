from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges


class BadgesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Badges
        fields = '__all__'

    def validate_name(self, value):
        """Ensure badge name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Badge name cannot be empty."})
        return value

