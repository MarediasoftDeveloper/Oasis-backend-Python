from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from app.Permissions.write_by_customer_and_venue_only import WriteByCustomerAndVenueOnly
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response

class Resent_OTP_For_Email_Verify(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, id):
        top_email_msg = 'We received a request to verify your Email. Enter the code below to continue your journey with My Oasis.'
        send_otp = Send_Otp_Mail(id, top_email_msg, subject='Your Email Verification Code')
        if send_otp:
            return Response({"message":"OTP has been resent to your email!"})

        
        return Response({"error":"sorry! something went wrong while sending you the email please try again later!"}) 



class Resent_OTP_For_Password_Reset(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, id):
        top_email_msg = (
            "We received a request to reset your password. "
            "Please verify it's you! Enter the code below to reset your password."
        )
        send_otp = Send_Otp_Mail(id, top_email_msg, subject='Reset Your Password')
        if send_otp:
            return Response({"message":"OTP has been resent to your email!"})

        
        return Response({"error":"sorry! something went wrong while sending you the email please try again!"}) 