from rest_framework import serializers
from app.Models.rewards_achiever import Rewards_Achiever

class RewardsAchieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rewards_Achiever
        fields = '__all__'

    def validate(self, data):
        """Ensure a customer can't claim the same reward multiple times."""
        customer = data.get('customer_taken')
        reward = data.get('reward')

        # Check only on creation (not update)
        if self.instance is None and Rewards_Achiever.objects.filter(customer_taken=customer, reward=reward).exists():
            raise serializers.ValidationError({
                "reward": "This reward has already been achieved by this customer."
            })
        return data

    def create(self, validated_data):
        """Create a new Rewards_Achiever record."""
        return Rewards_Achiever.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update existing Rewards_Achiever record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible custom logic later."""
        instance.delete()
