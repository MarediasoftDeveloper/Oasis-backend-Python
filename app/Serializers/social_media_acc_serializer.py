from rest_framework import serializers
from app.Models.social_media_accounts import Social_Media_Accounts

class SocialMediaAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social_Media_Accounts
        fields = '__all__'

    def validate_link(self, value):
        """Ensure the social media link is not empty and is a valid URL format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Social media link cannot be empty.")

        if not (value.startswith("http://") or value.startswith("https://")):
            raise serializers.ValidationError("Link must start with 'http://' or 'https://'.")
        return value

    def validate(self, data):
        """Prevent duplicate social media entries for the same user."""
        user = data.get('user')
        social_media = data.get('social_media')

        # When creating a new record
        if self.instance is None and Social_Media_Accounts.objects.filter(user=user, social_media=social_media).exists():
            raise serializers.ValidationError({
                "social_media": f"This user already has a {social_media} account linked."
            })
        return data

    def create(self, validated_data):
        """Create new social media account entry."""
        return Social_Media_Accounts.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing social media account."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic."""
        instance.delete()
