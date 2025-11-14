from rest_framework import serializers
from app.Models.raffles_entry import Raffles_Entry
from django.utils import timezone

class RafflesEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Raffles_Entry
        fields = '__all__'
        read_only_fields=['user']

    def validate(self, data):
        """Ensure a user can't join the same raffle multiple times."""
        user = self.context['request'].user
        raffle = data.get('raffle')

        # Only check on creation
        if self.instance is None and Raffles_Entry.objects.filter(user=user, raffle=raffle).exists():
            raise serializers.ValidationError({
                "error": "You have already joined this raffle."
            })
        if raffle.is_ended:
            raise serializers.ValidationError({
                "error": "This raffle has reached its deadline for entries please select another raffle!"
            })
        
        if raffle.start_at > timezone.now():
                raise serializers.ValidationError({
                    "error": "The raffle has not started yet."
                })

        # Check if the raffle has ended (ended_at <= current time)
        if raffle.ended_at < timezone.now():
            raise serializers.ValidationError({
                "error": "This raffle has ended. You can no longer join."
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
