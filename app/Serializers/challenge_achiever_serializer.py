from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from app.Models.challenge_achiever import Challenge_Achiever
from venue.models.challenges import Challenges

class ChallengeAchieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge_Achiever
        fields = '__all__'
        read_only_fields = ['scanned_at']  # automatically handled

    def validate(self, data):
        """Validate cooldown time and daily cap before allowing scan."""
        customer = data.get('customer_taken')
        challenge = data.get('challenge')

        if not challenge or not customer:
            raise serializers.ValidationError("Customer and Challenge are required fields.")

        # --- Check Cooldown Period ---
        last_entry = (
            Challenge_Achiever.objects
            .filter(customer_taken=customer, challenge=challenge)
            .order_by('-scanned_at')
            .first()
        )

        if last_entry:
            next_allowed_time = last_entry.scanned_at + timedelta(hours=challenge.cool_down_hours)
            if timezone.now() < next_allowed_time:
                remaining = next_allowed_time - timezone.now()
                hours, remainder = divmod(remaining.total_seconds(), 3600)
                minutes = remainder // 60
                raise serializers.ValidationError({
                    "cool_down": f"You can scan this challenge again in {int(hours)}h {int(minutes)}m."
                })

        # --- Check Daily Cap ---
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        daily_count = Challenge_Achiever.objects.filter(
            customer_taken=customer,
            challenge=challenge,
            scanned_at__gte=start_of_day,
            scanned_at__lt=end_of_day
        ).count()

        if daily_count >= challenge.daily_cap:
            raise serializers.ValidationError({
                "daily_cap": f"You have already reached the daily cap of {challenge.daily_cap} scans for this challenge."
            })

        return data

    def create(self, validated_data):
        """Create a new Challenge_Achiever record."""
        return Challenge_Achiever.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing Challenge_Achiever record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()
