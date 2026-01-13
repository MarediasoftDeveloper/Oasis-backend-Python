from rest_framework import serializers
from app.Models.users_interests import User_Interest
from app.Serializers.interests_serializer import InterestSerializer

class UserInterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = User_Interest
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_user(self, value):
        """Ensure a user can have only one User_Interest entry."""
        if self.instance is None and User_Interest.objects.filter(user=value).exists():
            raise serializers.ValidationError({"error":"User already has an interest record."})
        return value

    def validate(self, data):
        """Minimal cross-field validation."""
        interests = data.get('interests')
        if not interests or len(interests) == 0:
            raise serializers.ValidationError({"error": "At least one interest must be selected."})
        return data

    def create(self, validated_data):
        """Handle creation, including ManyToMany field."""
        interests = validated_data.pop('interests', [])
        instance = User_Interest.objects.create(**validated_data)
        instance.interests.set(interests)
        return instance

    def update(self, instance, validated_data):
        """Handle update safely with ManyToMany field support."""
        interests = validated_data.pop('interests', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if interests is not None:
            instance.interests.set(interests)

        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()


class UserInterestSerializerStaff(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    class Meta:
        model = User_Interest
        fields = '__all__'
        read_only_fields = ('user','interests')
