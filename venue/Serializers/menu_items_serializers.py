from rest_framework import serializers
from venue.models.menu import Menu_Items
from venue.models.menu_categories import Food_Menu_Category
from venue.Serializers.menu_category import FoodMenuCategorySerializer

class MenuItemsSerializer(serializers.ModelSerializer):
    menu_category = FoodMenuCategorySerializer(read_only=True)
    menu_category_id = serializers.PrimaryKeyRelatedField(
        queryset=Food_Menu_Category.objects.all(),
        required=False,
        write_only=True
    )
    class Meta:
        model = Menu_Items
        fields = '__all__'
        read_only_fields=['menu_category']
        

    def validate_item_name(self, value):
        """Ensure item name is not empty."""
        if value and not value.strip():
            raise serializers.ValidationError({"error":"Item name cannot be empty."})
        return value

    def validate_item_price(self, value):
        """Ensure price is non-negative."""
        if value and value < 0:
            raise serializers.ValidationError({"error":"Item price cannot be negative."})
        return value


    def validate_item_points(self, value):
        """Ensure points are non-negative (if provided)."""
        if value is not None and value < 0:
            raise serializers.ValidationError({"error":"Item points cannot be negative."})
        return value
    


    def create(self, validated_data):
        """Create new menu item."""
        category = validated_data.pop('menu_category_id', None)
        if category is not None:
            return Menu_Items.objects.create(menu_category=category,**validated_data)
        return Menu_Items.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """Update existing menu item."""
        category = validated_data.pop('menu_category_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if category is not None:
            instance.menu_category = category
        
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion (with future custom logic)."""
        instance.delete()
