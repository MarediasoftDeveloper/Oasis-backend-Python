from rest_framework import serializers
from app.Models.terms_and_conditions_accept import TermsAndConditionsAccept
from app.Serializers.customer_signup_serializer import Customer_Serializer


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    user = Customer_Serializer(read_only=True)
    class Meta:
        model = TermsAndConditionsAccept
        fields = '__all__'
        read_only_fields =['user']
