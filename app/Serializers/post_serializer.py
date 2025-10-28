from rest_framework import serializers
from app.Models.posts import Post
from app.Serializers.interests_serializer import InterestSerializer
from app.Models.interests import Customer_Interest
from django.utils.text import slugify


class PostSerializer(serializers.ModelSerializer):
    categories = InterestSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Customer_Interest.objects.all(),
        many=True,
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['user', 'slug', 'date']  # auto-handled fields
     
    def validate_image(self, value):
        """Ensure an image is provided."""
        if not value:
            raise serializers.ValidationError("An image is required for the post.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request.method =='POST':
            categories = data.get('categories')
            if not categories or len(categories) == 0:
                raise serializers.ValidationError({"categories": "At least one category must be selected."})
        
        return data

    def create(self, validated_data):
        """Create a new post with a generated slug and category handling."""
        categories = validated_data.pop('categories', [])
        instance = Post.objects.create(**validated_data)
        if not categories:
            instance.categories.add(1)
        else:
            instance.categories.add(categories)
        # Generate a unique slug
        base_slug = slugify(instance.caption or f"post-{instance.user.id}")
        slug = base_slug
        count = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{count}"
            count += 1
        instance.slug = slug
        instance.save()

        # Set categories (ManyToMany)
        instance.categories.set(categories)
        return instance

    def update(self, instance, validated_data):
        """Update post with category handling."""
        categories = validated_data.pop('categories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        return instance

    def delete(self, instance):
        """Allow deletion with future custom logic."""
        instance.delete()
