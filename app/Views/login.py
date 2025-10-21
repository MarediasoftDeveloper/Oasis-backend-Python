from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Customer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from app.Views.use_referral_code import UseReferralCode
from rest_framework import status

class Login(APIView):   

    permission_classes=[AllowAny]

    def post(self, request):
        
        data = request.data.get('credentials')
        email = data.get('email')
        password = data.get('password')
        referral_code = data.get('referral_code')
        if not email or not password:
            return Response({'error':"Credentials not provided!"})
    
        try:
            customer = Customer.objects.get(email=email)

            if not check_password(password, customer.password):
                return Response({'error': 'One or more information is incorrect!'}, status=401)

            customer_data = {
                'id': customer.id,
                'username': customer.username,
                'email': customer.email,
            }

            if referral_code:  # Only include if provided
                error_or_message = UseReferralCode(customer.id, referral_code)
                customer_data['referral_code_response'] = error_or_message
                if not error_or_message['status'] == 200:
                    return Response({"error":error_or_message['error']}, status=status.HTTP_400_BAD_REQUEST)
                    

            refresh = RefreshToken.for_user(customer)

            

            return Response({
                'customer': customer_data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=200)

        except Customer.DoesNotExist:
            return Response({'error': 'One or more information is incorrect!'}, status=401)

        except Exception as e:
            return Response({'error': str(e)}, status=500)



                        
                        
            


