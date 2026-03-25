from rest_framework import serializers
from app.Models.raffles_entry import Raffles_Entry
from venue.Serializers.raffles_serializer import RafflesSerializer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.utils import timezone


class GetRafflesEntrySerializerStaff(serializers.ModelSerializer):
    raffle = RafflesSerializer(read_only=True)
    user = CustomerProfileSerializer(source='user.customer_profile', read_only=True)

    class Meta:
        model = Raffles_Entry
        fields="__all__"
        read_only_fields=['raffle']