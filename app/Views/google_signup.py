from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from app.Models.customers import Customer

class Google_Signup(APIView):   


    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            try:
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
                # ...
            except ValueError as e:
                print("Google verification error:", str(e))  # 👈 add this
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            email = idinfo.get('email')
            name = idinfo.get('name')
            # picture = idinfo.get('picture')

            if not email:
                return Response({'error': 'Email not provided by Google'}, status=status.HTTP_400_BAD_REQUEST)

            #  Create or get customer
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={'username': name}
            )

            #  Generate JWT tokens
            refresh = RefreshToken.for_user(customer)
            
            # Response
            return Response({
                'customer': {
                    'id': customer.id,
                    'email': customer.email,
                    'username': customer.username,
                    # 'picture': picture,
                    'is_new_customer': created
                },
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            })

        except ValueError:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        