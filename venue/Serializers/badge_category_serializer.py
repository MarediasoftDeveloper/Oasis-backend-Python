from rest_framework import serializers
from venue.models.badge_category import Badge_Category

class BadgesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge_Category
        fields = '__all__'

    
    def validate_category(self, value):
        """Ensure badge category is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error":"Badge Category cannot be empty."})
        return value

    
    def validate_num_of_task_to_achieve_badge(self, value):
        """Ensure number of tasks is greater than zero."""
        if value <= 0:
            raise serializers.ValidationError({"error":"Number of tasks to achieve badge must be greater than 0."})
        return value