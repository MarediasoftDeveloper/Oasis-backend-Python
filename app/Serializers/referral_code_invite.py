from rest_framework import serializers
from app.Models.referrals import Referrals

class Referral_Code_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Referrals
        fields = '__all__'

    def validate_referral_code(self, value):
        """Ensure referral code is non-empty and alphanumeric."""
        if not value or not value.strip():
            raise serializers.ValidationError("Referral code cannot be empty.")
        if len(value) != 9:
            raise serializers.ValidationError("Referral code must be exactly 9 characters long.")
        if not value.isalnum():
            raise serializers.ValidationError("Referral code must be alphanumeric.")
        return value

    def validate(self, data):
        """Minimal logical checks."""
        sender = data.get('referral_code_sender')
        receiver = data.get('referral_code_user')

        # Ensure sender and receiver aren't the same user
        if sender and receiver and sender == receiver:
            raise serializers.ValidationError({
                'referral_code_user': "Sender and receiver cannot be the same user."
            })
        return data

    def create(self, validated_data):
        """Create a new referral record."""
        return Referrals.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing referral record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic."""
        instance.delete()
