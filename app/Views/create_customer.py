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
            top_email_msg = 'We received a request to verify your Email. Enter the code below to continue your journey with My Oasis.'
            mail_sent = Send_Otp_Mail(customer_id, top_email_msg, subject='Your Email Verification Code')
        
            if mail_sent:
                return Response(
                    {
                        "message": "Customer created successfully. OTP sent to your email.",
                        "customer": {
                            "id":response.data.get('id'),
                            "username":response.data.get('username'),
                            "email":response.data.get('email')
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
       
        return response