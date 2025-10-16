from rest_framework.serializers import ModelSerializer, EmailField
from rest_framework import serializers
from ..Models.referrals import Referrals
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password, check_password

class Referral_Code_Serializer(ModelSerializer):
    
    class Meta:
        model= Referrals
        fields = '__all__'

    