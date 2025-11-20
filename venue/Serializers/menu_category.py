from rest_framework import serializers
from venue.models.menu_categories import Food_Menu_Category
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.models import Customer

class FoodMenuCategorySerializer(serializers.ModelSerializer):
    venue = Customer_Serializer(read_only=True) 

    class Meta:
        model = Food_Menu_Category
        fields = '__all__'
        read_only_fields=['venue']

    def validate_name(self, value):
        """Ensure category name is not empty or just whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        return value

    def create(self, validated_data):
        """Create a new food menu category."""
        return Food_Menu_Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing food menu category."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()
