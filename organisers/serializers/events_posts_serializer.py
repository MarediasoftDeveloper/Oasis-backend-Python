from rest_framework import serializers
from app.Models.event_posts import EventPosts
from app.Models.posts import Post
from app.Models.events import Events
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Serializers.post_serializer import PostSerializer
from .events_serializer import EventAppSerializer
from django.db import transaction


class EventAppPostsSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(
            queryset=Events.objects.all(),
    )
    posts = PostSerializer(required=False)
    
    class Meta:
        model = EventPosts
        fields = '__all__'    


    def validate(self, attrs):
        post_data = attrs.get('posts')
        event = attrs.get('event')

        # 1️⃣ Check event exists
        if not event:
            raise serializers.ValidationError({
                "error": "Event is required."
            })

        # 2️⃣ Validate post data exists
        if not post_data:
            raise serializers.ValidationError({"error": "Post data is required."})

        # 3️⃣ Example: title required
        if not post_data.get('caption'):
            raise serializers.ValidationError({"error": "Caption is required."})
        
        return attrs

    def create(self, validated_data):
        post_data = validated_data.pop('posts')
        categories = post_data.pop('category_ids')
        categories = [cat.id for cat in categories]

        request = self.context.get('request')
        post = Post.objects.create(user=request.user, **post_data)
        post.categories.set(categories)
        event_post = EventPosts.objects.create(
            posts=post,
            **validated_data
        )
        return event_post


