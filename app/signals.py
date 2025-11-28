from django.db.models.signals import post_save
from django.dispatch import receiver
from app.Models.friendships import Friendships
from app.Views.utils.fcm import send_push_notification

@receiver(post_save, sender=Friendships)
def notify_friend_request(sender, instance, created, **kwargs):
    if created:
        receiver = instance.request_getter     # user receiving the request
        sender_user = instance.request_sender  # user sending the request

        send_push_notification(
            receiver,
            "New Friend Request",
            f"{sender_user.username} sent you a friend request",
            data={
                "type": "friend_request",
                "sender_id": str(sender_user.id)
            }
        )
