from rest_framework import serializers
from app.Models.social_media_accounts import Social_Media_Accounts



class SocialMediaAccountsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Social_Media_Accounts
        fields = '__all__'
        read_only_fields = ['user']

    def validate_link(self, value):
        """Ensure the social media link is valid."""
        if not value or not value.strip():
            raise serializers.ValidationError({"error": "Social media link cannot be empty."})

        if not (value.startswith("http://") or value.startswith("https://")):
            raise serializers.ValidationError({"error": "Link must start with http:// or https://"})
        return value

    def validate(self, data):
        """Prevent duplicate social media entries for the same user and limit count."""
        request = self.context.get('request')
        user = request.user if request else None
        social_media = data.get('social_media')

        if not user:
            raise serializers.ValidationError({"error":"User context missing."})

        # Exclude current instance when updating
        existing_accounts = Social_Media_Accounts.objects.filter(user=user)
        if self.instance:   
            existing_accounts = existing_accounts.exclude(id=self.instance.id)

        # Check for duplicates
        if existing_accounts.filter(social_media__iexact=social_media).exists():
            raise serializers.ValidationError({
                "error": f"You already have a {social_media} account linked."
            })

        # Check for limit (max 3)
        if existing_accounts.count() >= 3:
            raise serializers.ValidationError({
                "error": "You can only link up to 3 social media accounts."
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
