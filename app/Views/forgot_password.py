from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from app.Permissions.write_by_customer_and_venue_only import WriteByCustomerAndVenueOnly
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from app.models import Customer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

import logging

logger = logging.getLogger(__name__)

class Forgot_Password(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        top_email_msg = (
            "We received a request to reset your password. "
            "Please verify it's you! Enter the code below to reset your password."
        )

        if not email:
            return Response(
                {"success": False, "error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = Customer.objects.filter(email__iexact=email).first()
        if not customer:
            return Response(
                {"success": False, "error": "This email is not registered."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            mail_sent = Send_Otp_Mail(customer.id, top_email_msg, subject='Reset Your Password')
            if mail_sent:
                return Response(
                    {
                        "success": True,
                        "message": "OTP sent to your email.",
                        "customer": {
                            "id": customer.id,
                            "email": customer.email,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"success": False, "error": "Failed to send OTP. Try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error sending OTP to {email}: {str(e)}")
            return Response(    
                {"success": False, "error": "Sorry! Something went wrong. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



