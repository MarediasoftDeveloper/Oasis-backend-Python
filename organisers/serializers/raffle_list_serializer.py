from rest_framework import serializers
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.models.raffles import Raffles


class RaffleListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Raffles
        fields = ['id', 'title', 'venue']