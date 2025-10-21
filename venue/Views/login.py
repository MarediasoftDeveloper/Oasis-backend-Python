from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Customer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from app.Views.email.send_and_validate_email import Send_Otp_Mail

class Login(APIView):   

    permission_classes=[AllowAny]

    def post(self, request):

        data = request.data.get('credentials')
        email = data.get('email')
        password = data.get('password')
       
        if not email or not password:
            return Response({'error':"Credentials not provided!"})

        try:
            venue = Customer.objects.get(email=email)


            if not venue.user_role == '2':
                return Response({'error': 'One or more information is incorrect!'}, status=401)

            if not venue.is_verified:
                Send_Otp_Mail(venue.id)
                return Response({'error':"Your email is not verified, Please check our mail on your registered email to verify!"})

            if not check_password(password, venue.password):
                return Response({'error': 'One or more information is incorrect!'}, status=401)

            refresh = RefreshToken.for_user(venue)

            # Build customer data dynamically
            venue_data = {
                'id': venue.id,
                'username': venue.username,
                'email': venue.email,
            }


            return Response({
                'customer': venue_data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=200)

        except Customer.DoesNotExist:
            return Response({'error': 'One or more information is incorrect!'}, status=401)

        except Exception as e:
            return Response({'error': str(e)}, status=500)



                        
                        
            


