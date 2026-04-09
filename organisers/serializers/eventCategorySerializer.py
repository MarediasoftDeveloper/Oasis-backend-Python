from rest_framework import serializers
from app.Models.events import EventCategory
from venue.models.badges import Badges
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.Serializers.qr_info_serializer import VenueQRInfoSerializer
from django.utils import timezone
from venue.models.qr_info_model import QR_Info






class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = "__all__"
















