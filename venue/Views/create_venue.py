from rest_framework import generics 
from app.models import Customer
from venue.Serializers.venue_signup_serializer import Venue_SignUp_Serializer 
from rest_framework import status
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class Create_Venue(generics.CreateAPIView):

    queryset = Customer.objects.all()
    serializer_class = Venue_SignUp_Serializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            venue_id = response.data.get('id')
            top_email_msg = 'We received a request to verify your Email. Enter the code below to continue your journey with My Oasis.'
            mail_sent = Send_Otp_Mail(venue_id, top_email_msg, subject='Your Email Verification Code')
            
            if mail_sent:
                return Response(
                    {
                        "message": "Venue created successfully. OTP sent to your email.",
                        "Venue": {
                            "id":response.data.get('id'),
                            "username":response.data.get('username'),
                            "email":response.data.get('email')
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
       
        return response