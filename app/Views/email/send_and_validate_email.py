from rest_framework.views import APIView
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
import random
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from app.models import Customer 
from rest_framework.response import Response
from app.Serializers.customer_signup_serializer import Customer_Serializer
from app.Models.otp_requests import OTP_Code
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import AllowAny
# Create your views here.
def generate_otp():
    return str(random.randint(100000, 999999))



def Send_Otp_Mail(id):
        customer = get_object_or_404(Customer, id=id)
        
      
        otp = generate_otp()
        save_otp = OTP_Code.objects.create(customer=customer, otp=make_password(otp))
        serializer = Customer_Serializer(customer, many=False)
        to_email = serializer.data['email']
        
        subject = "Oasis - Your Email Verification Code"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [customer.email]

        # Render HTML content
        html_content = render_to_string('emails/oasis_otp_email.html', {
            'otp': otp
        })

        # # Optional plain-text fallback
        # text_content = f"Hello {customer.username}, your OTP is {otp}. It will expire in 10 minutes."

        # Create and send the email
        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


        return True


class Validate_mail(APIView):

    permission_classes = [AllowAny]

    def post(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        if customer.is_verified:
             return Response({"message": "Your Email is already verified!"})
        
        get_otp = OTP_Code.objects.filter(customer=customer).latest('created_at')
        entered_opt = request.data.get('otp')
        try:
            if get_otp.is_expired():    
                return Response({"message": "This code has been expired!"})
        except OTP_Code.DoesNotExist:
                return Response({"message": "No OTP found for this customer!"})
            
        

        if check_password(entered_opt, get_otp.otp):
            get_otp = OTP_Code.objects.filter(customer=customer).delete()
            customer.is_verified = True
            customer.save()
            return Response({"message": "Your email has been successfully Verified!"})

        return Response({"message": "Your OTP is wrong!"})
    


