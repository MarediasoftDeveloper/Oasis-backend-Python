from django.utils import timezone
from app.models import Customer   # adjust import
from app.Models.stamps import Stamps    # adjust import
from app.Views.utils.fcm import send_push_notification



def send_daily_notification():
    today = timezone.localtime().date()

    # users who ALREADY did today's stamp
    stamped_users = Stamps.objects.filter(
        stamped_at__date=today
    ).values_list('user_id', flat=True)

    receivers =list(Customer.objects.exclude(id__in=stamped_users))

    title = "⏰ don't forget to collect today's stamp!"
    body = "Here is your daily reminder — get your daily stamp and collect 30 points! 🎉🚀"

    send_push_notification(
        receivers,
        title,
        body,
        data={
            "type": "stamp_missed",
            "route": "/dailyStampsScreen",
        }
    )
