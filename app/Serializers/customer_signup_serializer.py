from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from app.models import Customer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password, check_password

class Customer_Serializer(ModelSerializer):
    
    def validate_email(self, value):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)

        if request and request.method == 'POST':
            if Customer.objects.filter(email__iexact=value):
                raise serializers.ValidationError('Email already exists')
            return value

        if instance:
            # If the user is keeping the same email — allow it
            if instance.email.lower() == value.lower():
                return value

            # If changing to another email — make sure it's unique
            if Customer.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("This email is already registered.")     
                
    class Meta:
        model = Customer
        fields = ['id','username', 'email', 'password']


    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(password)  # Hash if updated
        instance.save()
        return instance