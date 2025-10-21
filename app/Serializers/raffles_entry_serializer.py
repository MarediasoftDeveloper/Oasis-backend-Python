from rest_framework import serializers
from app.Models.raffles_entry import Raffles_Entry

class RafflesEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Raffles_Entry
        fields = '__all__'

    def validate(self, data):
        """Ensure a user can't join the same raffle multiple times."""
        user = data.get('user')
        raffle = data.get('raffle')

        # Only check on creation
        if self.instance is None and Raffles_Entry.objects.filter(user=user, raffle=raffle).exists():
            raise serializers.ValidationError({
                "raffle": "This user has already joined this raffle."
            })
        return data

    def create(self, validated_data):
        """Create a new raffle entry."""
        return Raffles_Entry.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing raffle entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()
