from rest_framework import serializers
from app.Models.friendships import Friendships
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    """A lightweight user serializer for showing basic info in friendships."""
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'email']

class FriendshipSerializer(serializers.ModelSerializer):
    """Serializer for Friendships model."""
    
    request_sender = UserMiniSerializer(read_only=True)
    request_getter = UserMiniSerializer(read_only=True)
    request_getter_id = serializers.PrimaryKeyRelatedField(
            source='request_getter',
            queryset=User.objects.all(),
            write_only=True
    )
    class Meta:
        model = Friendships
        fields = [
            'id',
            'request_sender',
            'request_getter',
            'request_getter_id',
            'send_on',
            'status',
            'accept_or_declined_on',
        ]
        read_only_fields = ['request_sender', 'send_on']

    
    def validate(self, attrs):
        """
        Check if the users are already friends or a request exists in either direction.
        """
        request = self.context.get("request")
        sender = request.user
        getter = attrs.get("request_getter")

        if request and request.method == 'POST':
            if sender == getter or sender.user_role in ['2', '3'] or getter.user_role in ['2', '3']:
                raise serializers.ValidationError("You cannot send a friend request to this user!")

            # Check for existing friendship or pending request (both directions)
            existing = Friendships.objects.filter(
                Q(request_sender=sender, request_getter=getter)
                | Q(request_sender=getter, request_getter=sender)
            ).exclude(status='declined')  # declined ones can be re-sent

            if existing.exists():
                raise serializers.ValidationError("A friendship or pending request already exists between these users.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['request_sender'] = request.user
        return super().create(validated_data)

