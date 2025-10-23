from rest_framework import serializers
from venue.models.menu import Menu_Items
from venue.Serializers.menu_category import FoodMenuCategorySerializer

class MenuItemsSerializer(serializers.ModelSerializer):
    menu_category = FoodMenuCategorySerializer()
    class Meta:
        model = Menu_Items
        fields = '__all__'
        

    def validate_item_name(self, value):
        """Ensure item name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Item name cannot be empty.")
        return value

    def validate_item_price(self, value):
        """Ensure price is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Item price cannot be negative.")
        return value

    def validate_item_quantity(self, value):
        """Ensure quantity is at least 1."""
        if value <= 0:
            raise serializers.ValidationError("Item quantity must be at least 1.")
        return value

    def validate_item_points(self, value):
        """Ensure points are non-negative (if provided)."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Item points cannot be negative.")
        return value

    def create(self, validated_data):
        """Create new menu item."""
        return Menu_Items.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update existing menu item."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion (with future custom logic)."""
        instance.delete()
