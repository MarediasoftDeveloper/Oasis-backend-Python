from rest_framework import serializers
from app.Models.referrals_Users import ReferralsUsers
from app.Models.referrals import Referrals
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Serializers.referral_code_invite import Referral_Code_Serializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ReferralSerializer(serializers.ModelSerializer):
    referral = Referral_Code_Serializer(read_only=True)
    code_user = Customer_Serializer(read_only=True)    
    
    class Meta:
        model = ReferralsUsers
        fields = '__all__'
        read_only_fields = ['referral', 'code_user']

