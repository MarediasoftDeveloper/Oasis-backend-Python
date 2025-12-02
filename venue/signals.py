from django.db.models.signals import post_save
from django.dispatch import receiver
from venue.models.challenges import Challenges
from venue.models.rewards import Rewards
from venue.models.raffles import Raffles
from app.models import Customer
from venue.models.venue_info import Venue_Info
from app.Views.utils.fcm import send_push_notification


@receiver(post_save, sender=Challenges) 
def notify_challenge_created(sender, instance, created, **kwargs):
    
    if created and instance.is_approved == 'approved':
        # All users → convert queryset to list
        receivers = list(Customer.objects.all())
        
        venue = Venue_Info.objects.get(venue=instance.venue)
        
        send_push_notification(
            receivers,
            f"🎯 New Challenge from {venue.venue_name}",
            "👉Hurry up! Don't be late to get your new badge 🎉.",
            data={
                "type": "challenge_created",  
                "route": "/allBadgesScreen", #venue_badges
                "venue_id": instance.venue.id, #venueId
                "venue_cover_image": venue.venue_cover_photo, #venueId
                "venue_title": venue.venue_name, #venueId
            }
        )





@receiver(post_save, sender=Rewards) 
def notify_reward_created(sender, instance, created, **kwargs):
    
    if created and instance.is_approved == 'approved':
        # All users → convert queryset to list
        receivers = list(Customer.objects.all())
        
        venue_name = Venue_Info.objects.get(venue=instance.venue).venue_name
        
        send_push_notification(
            receivers,
            f"🏆 New Reward from {venue_name}",
            "👉Hurry up! Don't be late to redeem your reward 🎉.",
            data={
                "type": "reward_created",  
                "route": "/rewardDetailScreen", #RewardsDetailScreen
                "reward_id": instance.id, #reward_id
            }
            )
        

@receiver(post_save, sender=Raffles) 
def notify_raffle_created(sender, instance, created, **kwargs):
    
    if created and instance.is_approved == 'approved':
        # All users → convert queryset to list
        receivers = list(Customer.objects.all())
        
        venue_name = Venue_Info.objects.get(venue=instance.venue).venue_name
        
        send_push_notification(
            receivers,
            f"🎟️ New Raffle from {venue_name}",
            "👉Hurry up! and participate in raffle to get exciting rewards 🎉.",
            data={
                "type": "raffle_created",  
                "route": "/rafflesDetailScreen", #RafflesDetailScreen
                "raffle_id": instance.id, #raffle_id
            }
            )