from django.shortcuts import render, redirect
from rest_framework import generics 
from app.models import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer 
from rest_framework import status
import random
from .email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class Create_Customer(generics.CreateAPIView):

    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            customer_id = response.data.get('id')
            mail_sent = Send_Otp_Mail(customer_id)
        
            if mail_sent:
                return Response(
                    {
                        "message": "Customer created successfully. OTP sent to your email.",
                        "customer": response.data
                    },
                    status=status.HTTP_201_CREATED
                )
       
        return response