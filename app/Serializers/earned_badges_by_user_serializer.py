from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from app.Models.earned_badges_by_user import Earned_Badges
from venue.Serializers.badges_serializer import BadgesSerializer

class Earned_Badges_By_User_Serializer(ModelSerializer):
    # Optional read-only fields for more descriptive responses
    badge = BadgesSerializer(read_only=True)
   
    class Meta:
        model = Earned_Badges
        fields = [
            'id',
            'user',
            'badge',
            'date', 
        ]
        read_only_fields = ['date']