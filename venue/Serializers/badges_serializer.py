from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges
from venue.models.badge_category import Badge_Category
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer
from django.db import transaction


class BadgesSerializer(serializers.ModelSerializer):
    # category = BadgesCategorySerializer()
    image = serializers.ImageField(write_only=True, required=True)
    class Meta:
        model = Badges
        fields = '__all__'

    def validate_name(self, value):
        """Ensure badge name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Badge name cannot be empty.")
        return value

   

    def create(self, validated_data):
        """Create a new badge and all its levels safely."""
        image = validated_data.pop('image', None)
        categories = Badge_Category.objects.all()

        with transaction.atomic():
            # Create the main badge
            badge = Badges.objects.create(**validated_data)

            # Create related levels for all categories
            for category in categories:
                BadgesLevel.objects.create(
                    image=image,
                    category=category,
                    badge=badge
                )

        return badge

    def update(self, instance, validated_data):
        """Update an existing badge."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic."""
        instance.delete()
