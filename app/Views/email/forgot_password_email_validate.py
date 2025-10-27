from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from app.Models.otp_requests import OTP_Code
from app.models import Customer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password


class Validate_forgot_Password_mail(APIView):

    permission_classes = [AllowAny]

    def post(self, request, id):
        customer = get_object_or_404(Customer, id=id)
      
        get_otp = OTP_Code.objects.filter(customer=customer).latest('created_at')
        entered_opt = request.data.get('otp')
        try:
            if get_otp.is_expired():    
                return Response({"error": "This code has been expired!"}, status=status.HTTP_400_BAD_REQUEST)
        except OTP_Code.DoesNotExist:
                return Response({"error": "No OTP found for this customer!"}, status=status.HTTP_400_BAD_REQUEST)
            
        

        if check_password(entered_opt, get_otp.otp):
            get_otp = OTP_Code.objects.filter(customer=customer).delete()
            return Response({"message": "Your email has been successfully Verified!"}, status=status.HTTP_200_OK)

        return Response({"error": "Your OTP is wrong!"}, status=status.HTTP_400_BAD_REQUEST)