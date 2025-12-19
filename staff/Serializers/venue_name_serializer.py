from rest_framework import serializers
from venue.models.venue_info import Venue_Info
from venue.Serializers.venue_signup_serializer import Venue_SignUp_Serializer


class VenueNameListSerializer(serializers.ModelSerializer):
    venue= Venue_SignUp_Serializer(read_only=True)
    
    class Meta:
        model = Venue_Info
        fields = ['venue_name', 'venue']
        