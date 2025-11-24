from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Customer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework.permissions import AllowAny
from rest_framework import status
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from venue.models.venue_info import Venue_Info
from venue.Serializers.venue_info_serializer import VenueInfoSerializer

class Login(APIView):   

    permission_classes=[AllowAny]

    def post(self, request):

        data = request.data.get('credentials')
        email = data.get('email')
        password = data.get('password')
        refresh_token = data.get('refresh')

        print(data)
       
        if not email or not password:
            return Response({'error':"Credentials not provided!"})

        try:
            venue_or_admin = Customer.objects.get(email__iexact=email)
           
            if not venue_or_admin.user_role in ['2', '3']:
                return Response({'error': 'One or more information is incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)
            
            elif venue_or_admin.user_role =='3': 
                if not check_password(password, venue_or_admin.password):
                    return Response({'error': 'One or more information is incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)
                if not venue_or_admin.is_verified:
                    return Response({'error': 'Your Admin account is under review please wait until it approved!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            if refresh_token:
                try:
                    old_refresh = RefreshToken(refresh_token)
                    old_refresh.blacklist()
                except TokenError:
                    pass  # Invalid or already blacklisted

                refresh = RefreshToken.for_user(venue_or_admin)

                admin_data = {
                    'id': venue_or_admin.id,
                    'email': venue_or_admin.email,
                    'user_role': venue_or_admin.user_role,
                }

                return Response({
                    'admin': admin_data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            
        
            venue_info = Venue_Info.objects.get(venue=venue_or_admin)
            serialized = VenueInfoSerializer(venue_info)
            if not venue_or_admin.is_verified:
                top_email_msg = 'We received a request to verify your Email. Enter the code below to continue your journey with My Oasis.'
                mail_sent = Send_Otp_Mail(venue_or_admin.id, top_email_msg, subject='Your Email Verification Code')
                return Response({'error':"Your email is not verified, Please check our mail on your registered email to verify!"}, status=status.HTTP_307_TEMPORARY_REDIRECT)
            if venue_info.status == 'pending':
                return Response({'error':"Your account is not approved, Please wait for approval."}, status=status.HTTP_406_NOT_ACCEPTABLE)
                

            if not check_password(password, venue_or_admin.password):
                return Response({'error': 'One or more information is incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)

            if refresh_token:
                try:
                    old_refresh = RefreshToken(refresh_token)
                    old_refresh.blacklist()
                except TokenError:
                    pass  # Invalid or already blacklisted

            refresh = RefreshToken.for_user(venue_or_admin)
            # Build customer data dynamically
            venue_data = {
                'id': venue_or_admin.id,
                'email': venue_or_admin.email,
                'user_role': venue_or_admin.user_role,
                'venue_info':{**serialized.data}
            }


            return Response({
                'venue': venue_data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response({'error': 'One or more information is incorrect!'}, status=401)

        except Exception as e:
            return Response({'error': str(e)}, status=500)



                        
                        
            


