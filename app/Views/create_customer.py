from django.shortcuts import render, redirect
from rest_framework.views import APIView 
from app.models import Customer
from app.models import Customer_profile
from app.Serializers.customer_signup_serializer import Customer_Serializer 
from rest_framework import status
import random
from .email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class Create_Customer(APIView):
    permission_classes=[AllowAny]
    
    def post(self, request):
        email = request.data.get('email')

        # Check if customer already exists (case-insensitive)
        customer = Customer.objects.filter(email__iexact=email).first()
        
        if customer:
            created = False
        else:
            customer = Customer.objects.create(email=email)
            created = True
        Customer_profile.objects.get_or_create(customer=customer)

        # Check password
        password_created = bool(customer.password and customer.has_usable_password())

        # --------------------------
        #  CASE 1: CUSTOMER EXISTS
        # --------------------------
        if not created:
            refresh = RefreshToken.for_user(customer)

            # CASE 1A — Exists but NOT verified
            if not customer.is_verified:
                
                top_email_msg = (
                    "We received a request to verify your Email. "
                    "Enter the code below to continue your journey with My Oasis."
                )
                
                mail_sent = Send_Otp_Mail(
                    customer.id,
                    top_email_msg,
                    subject='Your Email Verification Code'
                )

                if not mail_sent:
                    return Response({"error": "Something went wrong! Please try again."}, status=400)

                return Response({
                    "verified": False,
                    "password_created": password_created,
                    "customer_id": customer.id,
                    "message": "Email exists but is not verified. OTP sent.",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                })
            
            if customer.is_verified and not password_created:
                return Response({
                        "verified": customer.is_verified,
                        "password_created": password_created,
                        "customer_id": customer.id,
                        "message": "Email exists and also verified, Please create your password to logged In.",
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh)
                })

            return Response({
                "verified": customer.is_verified,
                "password_created": password_created,
                "customer_id": customer.id,
                "message": "Email exists and also verified, Please proceed to login.",
            })
        
        top_email_msg = 'We received a request to verify your Email. Enter the code below to continue your journey with My Oasis.'
        mail_sent = Send_Otp_Mail(customer.id, top_email_msg, subject='Your Email Verification Code')
          
        
        if not mail_sent:
            return Response({"error": "Something went wrong! Please try again."}, status=400)

        refresh = RefreshToken.for_user(customer)

        return Response({
            "message": "Customer created successfully. OTP sent to email.",
            "customer": {
                "id": customer.id,
                "email": customer.email
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        }, status=201)
   
       
        
        
        