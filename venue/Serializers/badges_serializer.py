from rest_framework import serializers
from venue.models.badges import Badges
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer

class BadgesSerializer(serializers.ModelSerializer):
    # category = BadgesCategorySerializer()
    class Meta:
        model = Badges
        fields = '__all__'

    def validate_name(self, value):
        """Ensure badge name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Badge name cannot be empty.")
        return value

    def validate_points_per_task(self, value):
        """Ensure points per task are non-negative."""
        if value < 0:
            raise serializers.ValidationError("Points per task cannot be negative.")
        return value

    def create(self, validated_data):
        """Create a new badge."""
        return Badges.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing badge."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic."""
        instance.delete()
