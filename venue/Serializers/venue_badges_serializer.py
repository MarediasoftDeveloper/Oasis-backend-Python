from rest_framework import serializers
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import Badges
import re
from app.Serializers.customer_signup_serializer import Customer_Serializer
from venue.Serializers.badges_serializer import BadgesSerializer


class VenueBadgesSerializer(serializers.ModelSerializer):
    venue= Customer_Serializer(read_only=True)    
    badge= BadgesSerializer(read_only=True)
    
    venue_badge = serializers.PrimaryKeyRelatedField(
        queryset=Badges.objects.all(),
        required=True,
        write_only=True
    )
    
    class Meta:
        model = Venue_Badges
        fields = '__all__'
        read_only_fields =['venue', 'venue_badge']

   
   
    def create(self, validated_data):
        """Create a new Challenge."""
        venue = self.context.get('request').user
        badge = validated_data.pop('venue_badge')
        

        venue_badge = Venue_Badges.objects.create(
            venue=venue,
            badge=badge,
        )
      
        
        return venue_badge