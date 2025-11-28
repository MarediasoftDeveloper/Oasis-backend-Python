import firebase_admin
from firebase_admin import messaging
from app.Models.DeviceFcmToken import DeviceFCM
from app.Models.notifications import Notifications

from firebase_admin import messaging

def send_push_notification(users, title, body, data=None):

    # Accept single user
    if not isinstance(users, (list, tuple, set)):
        users = [users]

    # Get all FCM tokens
    tokens = list(
        DeviceFCM.objects.filter(user__in=users)
        .values_list("fcm_token", flat=True)
    )

    # Save notifications in DB in batch
    Notifications.objects.bulk_create(
        [Notifications(user=u, title=title, body=body) for u in users]
    )

    if not tokens:
        return {"error": "No device tokens available"}

    # FCM: Batch limit = 500 tokens
    chunks = [tokens[i:i + 500] for i in range(0, len(tokens), 500)]

    results = []

    for batch in chunks:
        message = messaging.MulticastMessage(
            tokens=batch,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
        )

        response = messaging.send_each_for_multicast(message)
        results.append(response)

    return results

