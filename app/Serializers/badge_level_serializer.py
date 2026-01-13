from rest_framework import serializers
from venue.models.badges import BadgesLevel, Badges
from venue.models.badge_category import Badge_Category
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer

class BadgesLevelSerializer(serializers.ModelSerializer):
    badge = BadgesSerializer(read_only=True)
    category = BadgesCategorySerializer(read_only=True)

    # Write-only fields
    level_name = serializers.CharField(max_length=40, write_only=True, required=True)
    num_of_task_to_achieve_badge = serializers.IntegerField(write_only=True, required=True)

    badge_id = serializers.PrimaryKeyRelatedField(
        source="badge",
        queryset=Badges.objects.all(),
        write_only=True,
    )

    class Meta:
        model = BadgesLevel
        fields = [
            "id",
            "badge",
            "category",
            "image",
            "points_per_task",
            "level_name",
            "num_of_task_to_achieve_badge",
            "badge_id",
        ]
        read_only_fields = ["badge", "category"]

    # ---------------------------
    # Field-level validation
    # ---------------------------

    def validate_num_of_task_to_achieve_badge(self, value):
        if value <= 0:
            raise serializers.ValidationError({"error":"Tasks required must be greater than zero."})
        return value

    def validate_points_per_task(self, value):
        if value < 0:
            raise serializers.ValidationError({"error":"Points per task cannot be negative."})
        return value

    # ---------------------------
    # Object-level validation
    # ---------------------------

    def validate(self, attrs):
        badge = attrs.get("badge")  # from badge_id source="badge"

        # Category does not exist yet; it is created in create()
        level_name = attrs.get("level_name")
        badge_level_name = f"{badge.name + " " + level_name}"
        print(badge_level_name)
        if self.context.get('request') == 'POST':
            if BadgesLevel.objects.filter(
                badge=badge,
                category__category__icontains=badge_level_name
            ).exists():
                raise serializers.ValidationError({"error":"This badge already has this category level."})

        return attrs

    # ---------------------------
    # CREATE
    # ---------------------------

    def create(self, validated_data):
        level_name = validated_data.pop("level_name")
        num_tasks = validated_data.pop("num_of_task_to_achieve_badge")

        badge = validated_data.pop("badge")
        badge_level_name = f"{badge.name + " " + level_name}"

        print(badge_level_name)
        # Create new category
        category_obj = Badge_Category.objects.create(
            category=badge_level_name,
            num_of_task_to_achieve_badge=num_tasks,
        )

        return BadgesLevel.objects.create(
            badge=badge,
            category=category_obj,
            **validated_data
        )

    # ---------------------------
    # UPDATE
    # ---------------------------

    def update(self, instance, validated_data):
        level_name = validated_data.pop("level_name", None)
        num_tasks = validated_data.pop("num_of_task_to_achieve_badge", None)
        badge = validated_data.pop("badge", None)
        badge_level_name = f"{badge.name + " " + level_name}"
        
        # Update category only if changed
        if not badge_level_name == instance.category.category:
            instance.category.category = badge_level_name
            instance.category.save()
            # category_obj = Badge_Category.objects.create(
            #     category=category_name,
            #     num_of_task_to_achieve_badge=num_tasks,
            # )
        elif not num_tasks == instance.category.num_of_task_to_achieve_badge:
            instance.category.num_of_task_to_achieve_badge = num_tasks
            instance.category.save()
            
        
        # Update badge if changed
        if badge:
            instance.badge = badge

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

   
     
    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()








#      badge_name = validated_data.pop('badge_name')
#         badge_description = validated_data.pop('badge_description', None)

# badge=None
#         if badge_description is not None: 
#             badge = Badges.objects.create(name=badge_name, description=badge_description)
#         else:
#             badge = Badges.objects.create(name=badge_name) 



