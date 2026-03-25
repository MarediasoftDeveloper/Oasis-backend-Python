from rest_framework import serializers
from app.Models.reporting_and_complains import ReportingAndComplains
from app.Models.posts import Post
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Serializers.post_serializer import PostSerializer

from django.contrib.auth import get_user_model

User = get_user_model()

class ReportAndComplainSerializer(serializers.ModelSerializer):
    reportedBy = Customer_Serializer(read_only=True)

    reportedUser = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        required=False
    )
    class Meta:
        model = ReportingAndComplains
        fields = '__all__'
        read_only_fields = ['reportedBy']

    def validate(self, attrs):
        request = self.context['request']

        # Prevent blocking yourself
        if attrs['reportedUser'] == request.user:
            raise serializers.ValidationError({"error":"You cannot report yourself."})

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['reportedBy'] = request.user
        return super().create(validated_data)
    




class ReportAndComplainListSerializer(serializers.ModelSerializer):
    reportedBy = Customer_Serializer()
    reportedUser = Customer_Serializer(read_only=True)
    post = PostSerializer()

    class Meta:
        model = ReportingAndComplains
        fields = '__all__'
        read_only_fields = ['reportedBy']