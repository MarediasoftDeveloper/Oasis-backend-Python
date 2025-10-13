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
from django.contrib.auth.hashers import make_password

# Create your views here.
def generate_otp():
    return str(random.randint(100000, 999999))



@api_view(['GET'])
def Save_otp_Send_mail(request, id):
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







    return Response({"customer": serializer.data})










