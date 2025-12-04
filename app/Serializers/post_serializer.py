from rest_framework import serializers
from app.Models.posts import Post
from app.Serializers.interests_serializer import InterestSerializer
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Models.interests import Customer_Interest
from app.Models.post_venues_tags import PostVenueTag
from venue.models.venue_info import Venue_Info
from rest_framework.response import Response
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from django.utils.text import slugify


class PostSerializer(serializers.ModelSerializer):
    categories = InterestSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Customer_Interest.objects.all(),
        many=True,
        write_only=True
    )
    tagged_venues = serializers.SerializerMethodField(required=False)
    
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['user', 'slug', 'date', 'time']

    def to_representation(self, instance):
        """Customize user data based on role."""
        data = super().to_representation(instance)

        if instance.user.user_role == '2':  # Venue
            data['user'] = VenueInfoSerializer(instance.user.venue_profile).data
        else:  # Customer
            data['user'] = CustomerProfileSerializer(instance.user.customer_profile).data

        return data
   
   
    def validate_image(self, value):
        """Ensure an image is provided."""
        if not value:
            raise serializers.ValidationError("An image is required for the post.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            category_ids = data.get('category_ids')
            if not category_ids or len(category_ids) == 0:
                raise serializers.ValidationError(
                    {"categories": "At least one category must be selected."}
                )
        return data
    
    def get_tagged_venues(self, instance):
        tag = PostVenueTag.objects.filter(post=instance).first()
        if not tag:
            return None

        venue = tag.venue
        return {
            "id": venue.id,
            "name": venue.venue_name,
            "image": venue.image.url if venue.image else None
        }


    def create(self, validated_data):
        """Create a new post with slug and categories."""
        request = self.context.get('request')
        category_ids = validated_data.pop('category_ids', [])
        
        instance = Post.objects.create(**validated_data)
        
        if request.user.user_role == "1":
            tagged_venue = request.data.get("tagged_venue")

            if tagged_venue:
                venue = Venue_Info.objects.filter(id=tagged_venue).first()
                if venue:
                    PostVenueTag.objects.create(post=instance, venue=venue)

        # Default category if none
        if category_ids:
            instance.categories.set(category_ids)
        else:
            instance.categories.clear()
       
        instance.save()
        return instance

       

    def update(self, instance, validated_data):
        """Update post and handle category updates."""
        category_ids = validated_data.pop('category_ids', None)
        request = self.context.get('request')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if request.user.user_role == "1":
            tagged_venue = request.data.get("tagged_venue")

            if tagged_venue:
                venue = Venue_Info.objects.filter(id=tagged_venue).first()
                if venue:
                    PostVenueTag.objects.create(post=instance, venue=venue)

        if category_ids is not None:
            instance.categories.set(category_ids)

        return instance


    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()
