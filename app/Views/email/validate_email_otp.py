from django.views import View
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
import random
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from app.Models.customers import Customer 
from rest_framework.response import Response
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Models.otp_requests import OTP_Code
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone



@api_view(['POST'])
def Validate_Mail_Otp(request, id):
    customer = get_object_or_404(Customer, id=id)
    get_otp = OTP_Code.objects.filter(customer=customer).latest('created_at')
    entered_opt = request.data.get('otp')
    try:
        if get_otp.is_expired():    
            return Response({"message": "This code has been expired!"})
    except OTP_Code.DoesNotExist:
            return Response({"message": "No OTP found for this customer!"})
        
    

    if check_password(entered_opt, get_otp.otp):
        get_otp = OTP_Code.objects.filter(customer=customer).delete()
        return Response({"message": "Your email has been successfully Verified!"})

    return Response({"message": "Your OTP is wrong!"})
    

    



