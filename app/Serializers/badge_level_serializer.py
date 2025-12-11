from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges
from venue.models.badge_category import Badge_Category
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer

class BadgesLevelSerializer(serializers.ModelSerializer):
    badge = BadgesSerializer(read_only=True)
    category = BadgesCategorySerializer(read_only=True)

    category_name = serializers.CharField(max_length=40, write_only=True, required=True)
    num_of_task_to_achieve_badge = serializers.IntegerField(write_only=True, required=True)

    badge_id = serializers.PrimaryKeyRelatedField(
        source=badge,
        queryset=Badges.objects.all(),
        write_only=True, 
    )

    class Meta:
        model = BadgesLevel
        fields = ['id', 'badge', 'category', 'image', 'points_per_task', 'category_name', 'num_of_task_to_achieve_badge', 'badge_id']
        read_only_fields=['category', 'badge']

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
    
    def validate_points_per_task(self, value):
        """Ensure points per task are non-negative."""
        if value < 0:
            raise serializers.ValidationError("Points per task cannot be negative.")
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
    
    def create(self, validated_data):
        category_name = validated_data.pop('category_name')
        num_of_task_to_achieve_badge = validated_data.pop('num_of_task_to_achieve_badge')
        
        badge_name = validated_data.pop('badge_name')
        badge_description = validated_data.pop('badge_description', None)
        badge=None
        if badge_description is not None: 
            badge = Badges.objects.create(name=badge_name, description=badge_description)
        else:
            badge = Badges.objects.create(name=badge_name) 

        category_saved = Badge_Category.objects.get_or_create(category=category_name, num_of_task_to_achieve_badge=num_of_task_to_achieve_badge)    
        
        

        return BadgesLevel.objects.create(category=category_saved, **validated_data)
