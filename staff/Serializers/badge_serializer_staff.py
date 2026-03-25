from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges
from venue.models.badge_category import Badge_Category
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer
from app.Serializers.badge_level_serializer import BadgesLevelSerializer 

class BadgesSerializerStaff(serializers.ModelSerializer):
    badge_levels = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Badges
        fields = "__all__"
        read_only_fields=['badge_levels']
        
    def get_badge_levels(self, obj):
        badge_levels = BadgesLevel.objects.filter(badge=obj)
        return BadgesLevelSerializer(badge_levels, many=True).data
    
    def validate_name(self, value):
        """Ensure badge name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Badge name cannot be empty."})
        return value

    


