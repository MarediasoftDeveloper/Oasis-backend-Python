from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges
from venue.models.badge_category import Badge_Category
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer

class BadgesLevelSerializer(serializers.ModelSerializer):
    badge = BadgesSerializer()
    category = BadgesCategorySerializer()

    class Meta:
        model = BadgesLevel
        fields = ['id', 'badge', 'category', 'image']

    # ---------------------------------------
    # Field-level validation
    # ---------------------------------------

    def validate_badge(self, value):
        if not Badges.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Badge does not exist.")
        return value

    def validate_category(self, value):
        if not Badge_Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Category does not exist.")
        return value

    def validate_image(self, value):
        if value is None:
            raise serializers.ValidationError("Image is required.")
        # Max size validation (optional)
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Image size cannot exceed {max_size_mb}MB.")
        return value

    # ---------------------------------------
    # Object-level validation (cross-field)
    # ---------------------------------------

    def validate(self, attrs):
        badge = attrs.get("badge")
        category = attrs.get("category")

        # Prevent duplicate badge/category pairs
        if BadgesLevel.objects.filter(badge=badge, category=category).exists():
            raise serializers.ValidationError(
                "This badge already has a level for the selected category."
            )

        return attrs