from rest_framework import serializers
from rest_framework import status

from django.utils import timezone
from datetime import timedelta
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.earned_badges_by_user import Earned_Badges
from venue.models.challenges import Challenges
from venue.models.venue_badges import Venue_Badges
from rest_framework.response import Response
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from venue.Serializers.challenge_serializer import ChallengesSerializer
from app.Views.functions.get_level_of_user_badge import get_level_points_per_task_and_save_it
from venue.models.badge_category import Badge_Category

class ChallengeAchieverSerializer(serializers.ModelSerializer):

    code = serializers.CharField(write_only=True, required=True)
    customer_taken = CustomerProfileSerializer(source='customer_taken.customer_profile', read_only=True)
    challenge = ChallengesSerializer(read_only=True)
    class Meta:
        model = Challenge_Achiever
        fields = '__all__'
        read_only_fields = ['scanned_at', 'customer_taken']  # automatically handled

    def validate(self, data):
        """Validate cooldown time and daily cap before allowing scan."""
        request = self.context.get('request')
        code = data.get('code')
        challenge = Challenges.objects.get(qr_code__code=code)
        venue_badge_obj = challenge.badge
        
        if not challenge:
            raise serializers.ValidationError("Invalid QR Code")
        
        user = request.user
        
     

            

        

        now = timezone.now()  # Use timezone aware current time
    
        # --- Check if Challenge hasn't started yet ---
        if now < challenge.starting_at:
            raise serializers.ValidationError({
                "error": f"This challenge will start on {challenge.starting_at}."
            })

        if challenge.is_ended:
            if venue_badge_obj.is_active:
                venue_badge_obj.is_active = False
                venue_badge_obj.save()
                
            raise serializers.ValidationError({
                "error": f"This challenge ended on {challenge.ending_at}."
            })

        # --- Check if Challenge already ended ---
        if now > challenge.ending_at:
            challenge.is_ended = True
            challenge.save()
            venue_badge_obj.is_active = False
            venue_badge_obj.save()
            raise serializers.ValidationError({
                "error": f"This challenge ended on {challenge.ending_at}."
            })
        
       
        
        # --- Check Cooldown Period ---
        last_entry = (
            Challenge_Achiever.objects
            .filter(customer_taken=user, challenge=challenge)
            .order_by('-scanned_at')
            .first()
        )

        if last_entry:
            # Cooldown in minutes instead of hours
            next_allowed_time = last_entry.scanned_at + timedelta(minutes=challenge.cool_down_minutes)

            if timezone.now() < next_allowed_time:  
                remaining = next_allowed_time - timezone.now()
                total_minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)

                raise serializers.ValidationError({
                    "error": f"You can scan this challenge again in {total_minutes}m {seconds}s."
                })

        # if last_entry:
        #     next_allowed_time = last_entry.scanned_at + timedelta(hours=challenge.cool_down_hours)
        #     if timezone.now() < next_allowed_time:
        #         remaining = next_allowed_time - timezone.now()
        #         hours, remainder = divmod(remaining.total_seconds(), 3600)
        #         minutes = remainder // 60
        #         raise serializers.ValidationError({
        #             "error": f"You can scan this challenge again in {int(hours)}h {int(minutes)}m."
        #         })

        # --- Check Daily Cap ---
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        daily_count = Challenge_Achiever.objects.filter(
            customer_taken=user,
            challenge=challenge,
            scanned_at__gte=start_of_day,
            scanned_at__lt=end_of_day
        ).count()

        if daily_count >= challenge.daily_cap:
            raise serializers.ValidationError({
                "error": f"You have already reached the daily cap of {challenge.daily_cap} scans for this challenge."
            })

        current_time = timezone.localtime(timezone.now()).time()  # Get current local time

        # Ensure daily_open_time and daily_close_time are provided and are valid
        # if challenge.daily_open_time and challenge.daily_close_time:
        #     if not (challenge.daily_open_time <= current_time <= challenge.daily_close_time):
        #         raise serializers.ValidationError({
        #             "error": f"The challenge is only available between {challenge.daily_open_time} and {challenge.daily_close_time}."
        #         })
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        code = validated_data.pop('code')
        try:
            challenge = Challenges.objects.get(qr_code__code__iexact=code)
        except Challenges.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid QR code!"})


        #  Add points to user
        actual_badge = challenge.badge.badge
     
        points = get_level_points_per_task_and_save_it(user, actual_badge)
    
        validated_data['customer_taken'] = user
        validated_data['challenge'] = challenge
        validated_data['points_issued'] = points
        achievement = Challenge_Achiever.objects.create(**validated_data)
        
        return achievement

    def update(self, instance, validated_data):
        """Update an existing Challenge_Achiever record."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Allow deletion with possible future custom logic."""
        instance.delete()






