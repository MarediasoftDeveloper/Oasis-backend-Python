from rest_framework import serializers
from venue.models.qr_info_model import QR_Info

class QRInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR_Info
        exclude=['code', 'qr_image']
    def validate_winning_points(self, value):
        """Ensure winning points are positive."""
        if value < 0:
            raise serializers.ValidationError("Winning points cannot be negative.")
        return value

    def validate(self, data):
        """Check logical consistency of expiration dates."""
        expires_at = data.get('expires_at')
        created_at = data.get('created_at')

        if expires_at and created_at and expires_at < created_at:
            raise serializers.ValidationError({
                'expires_at': 'Expiration date cannot be earlier than creation date.'
            })
        return data

    def create(self, validated_data):
        """Create QR_Info entry."""
        return QR_Info(**validated_data)

    def update(self, instance, validated_data):
        """Update QR_Info entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()



class VenueQRInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR_Info
        fields="__all__"

        
    def validate_winning_points(self, value):
        """Ensure winning points are positive."""
        if value < 0:
            raise serializers.ValidationError("Winning points cannot be negative.")
        return value

    def validate(self, data):
        """Check logical consistency of expiration dates."""
        expires_at = data.get('expires_at')
        created_at = data.get('created_at')

        if expires_at and created_at and expires_at < created_at:
            raise serializers.ValidationError({
                'expires_at': 'Expiration date cannot be earlier than creation date.'
            })
        return data

    def create(self, validated_data):
        """Create QR_Info entry."""
        return QR_Info(**validated_data)

    def update(self, instance, validated_data):
        """Update QR_Info entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()
