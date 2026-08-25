import firebase_admin
from firebase_admin import messaging
from app.Models.DeviceFcmToken import DeviceFCM
from app.Models.notifications import Notifications
from django.db.models import QuerySet
from firebase_admin import messaging

def send_push_notification(users, title, body, data=None):

    # Accept single user
    if not isinstance(users, (list, tuple, set)):
        users = [users]

    # Get all FCM tokens
    tokens = list(
        DeviceFCM.objects.filter(user__in=users)
        .exclude(fcm_token="")
        .values_list("fcm_token", flat=True)
    )

    # Save notifications in DB in batch
    Notifications.objects.bulk_create(
        [Notifications(user=u, title=title, body=body, data=data) for u in users]
    )

    if not tokens:
        return {"error": "No device tokens available"}

    # FCM: Batch limit = 500 tokens
    chunks = [tokens[i:i + 500] for i in range(0, len(tokens), 500)]

    results = []

    for batch in chunks:
        message = messaging.MulticastMessage(
            tokens=batch,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    )
                )
            ),
            data=data or {},
        )

        response = messaging.send_each_for_multicast(message)
        results.append(response)

    return results




def send_push_posts_notification(users, title, body, data=None, image=None):
    # Convert queryset / single user / etc.
    if isinstance(users, QuerySet):
        users = list(users)
    elif not isinstance(users, (list, tuple, set)):
        users = [users]

    tokens = list(
        DeviceFCM.objects.filter(user__in=users)
        .exclude(fcm_token="")
        .values_list("fcm_token", flat=True)
    )
    if not tokens:
        return

    # Save notifications in DB
    Notifications.objects.bulk_create([Notifications(user=u, title=title, body=body, data=data, image=image) for u in users])

    # Create APNS payload for iOS
    apns = messaging.APNSConfig(
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(
                    title=title,
                    body=body
                ),
                mutable_content=True  # Required for rich notifications on iOS
            )
        ),
        fcm_options=messaging.APNSFCMOptions(
            image=image  # Full image URL
        )
    )

    # Prepare the message for iOS + Android
    chunks = [tokens[i:i+500] for i in range(0, len(tokens), 500)]

    for batch in chunks:
        message = messaging.MulticastMessage(
            tokens=batch,
            notification=messaging.Notification(title=title, body=body, image=image),
            data=data or {},
            apns=apns  # 👍 Proper iOS format
        )

        messaging.send_each_for_multicast(message)