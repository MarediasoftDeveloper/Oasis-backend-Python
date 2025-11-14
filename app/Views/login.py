from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Customer, Customer_profile
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import AllowAny
from app.Views.use_referral_code import UseReferralCode
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class Login(APIView):   

    permission_classes=[AllowAny]

    def post(self, request):
        
        data = request.data.get('credentials')
        email = data.get('email')
        password = data.get('password')
        referral_code = data.get('referral_code')
        refresh_token = data.get('refresh')

        if not email or not password:
            return Response({'error':"Credentials not provided!"})
    
        try:
            customer = Customer.objects.get(email=email, user_role='1')

            if not password:
                return Response({'error': 'Password is required!'}, status=401)
            
            
            if not check_password(password, customer.password):
                return Response({'error': 'One or more information is incorrect!'}, status=401)



            # Optional referral handling
            customer_data = {}
            if referral_code:   
                error_or_message = UseReferralCode(customer.id, referral_code)
                customer_data['referral_code_response'] = error_or_message
                if error_or_message.get('status') != 200:
                    return Response({"error": error_or_message['error']}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Safely handle refresh token blacklist
            if refresh_token:
                try:
                    old_refresh = RefreshToken(refresh_token)
                    old_refresh.blacklist()
                except TokenError:
                    pass  # Invalid or already blacklisted

            # ✅ Generate new token pair
            refresh = RefreshToken.for_user(customer)

            # ✅ Serialize customer profile
            customer_profile, _ = Customer_profile.objects.get_or_create(customer=customer)
            serialized = CustomerProfileSerializer(customer_profile)

            return Response({
                **serialized.data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                **customer_data
            }, status=200)

        except Customer.DoesNotExist:   
            return Response({'error': 'One or more information is incorrect!'}, status=401)


                        
                        
            


