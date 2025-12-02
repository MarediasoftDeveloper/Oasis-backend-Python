from django.db.models.signals import post_save
from django.dispatch import receiver
from app.Models.friendships import Friendships
from app.Models.posts import Post
from app.models import Customer
from venue.models.venue_info import Venue_Info
from app.Views.utils.fcm import send_push_notification
from django.db.models import Q

@receiver(post_save, sender=Friendships)
def notify_friend_request(sender, instance, created, **kwargs):
    if created:
        receiver = instance.request_getter     # user receiving the request
        sender_user = instance.request_sender  # user sending the request

        send_push_notification(
            receiver,
            "👨‍👨 New Friend Request",
            f"🤗 {sender_user.username} sent you a friend request",
            data={
                "type": "friend_request",
                "route":"/socialUserProfileScreen",
                "user_id": str(sender_user.id)
            }
        )


@receiver(post_save, sender=Friendships)
def notify_friend_request_accepted(sender, instance, created, **kwargs):
    # Only act on updates (not creation)
    if not created and instance.status == "accepted":

        receiver = instance.request_sender  # user who originally SENT request
        accepter = instance.request_getter  # user who accepted
        
        send_push_notification(
            receiver,
            "🤝 Friend Request Accepted",
            f"🤗 {accepter.username} accepted your friend request",
            data={
                "type": "friend_request",
                "route":"/socialUserProfileScreen",
                "user_id": str(accepter.id)
            }
        )




@receiver(post_save, sender=Post)
def notify_post_upload(sender, instance, created, **kwargs):
    # Only notify on creation
    if created and instance.user.user_role == "1":

        # Get all accepted friendships
        friendships = Friendships.objects.filter(
            Q(request_sender=instance.user, status='accepted') |
            Q(request_getter=instance.user, status='accepted')
        )

        # Extract friend users
        friends = set()
        for f in friendships:
            if f.request_sender == instance.user:
                friends.add(f.request_getter)
            else:
                friends.add(f.request_sender)

        receivers = list(friends)

        send_push_notification(
            receivers,
            "A New Post Created!",
            f"{instance.user.username} has created a new post.",
            data={
                "type": "post_created",
                "route": "/postDetailScreen",
                "slug": str(instance.slug),
                "image": instance.image.url,
            }
        )

    elif created and instance.user.user_role == "2":

        receivers = list(Customer.objects.all())  # Fix variable name
        venue = Venue_Info.objects.filter(customer=instance.user).first()  # Fix queryset issue

        venue_name = venue.venue_name if venue else instance.user.username  # Fallback

        send_push_notification(
            receivers,
            "A New Post Created!",
            f"{venue_name} has created a new post.",
            data={
                "type": "post_created",
                "route": "/postDetailScreen",
                "slug": str(instance.slug),
                "image": instance.image.url,
            }
        )
