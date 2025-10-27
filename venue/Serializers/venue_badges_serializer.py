from rest_framework import serializers
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import Badges
import re
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.Serializers.badges_serializer import BadgesSerializer


class VenueBadgesSerializer(serializers.ModelSerializer):
    venue= Customer_Serializer()    
    badge= BadgesSerializer()
    
    class Meta:
        model = Venue_Badges
        fields = '__all__'

   