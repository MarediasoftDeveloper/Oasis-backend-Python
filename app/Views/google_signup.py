from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.permissions import AllowAny
from app.models import Customer_profile
from app.Models.DeviceFcmToken import DeviceFCM
from app.Models.terms_and_conditions_accept import TermsAndConditionsAccept
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Models.user_current_app_version import UserCurrentAppVersion


User = get_user_model()

class Google_Signup(APIView):
    
   permission_classes=[AllowAny]

   def post(self, request):
        id_token_value = request.data.get("id_token")
        fcm_token = request.data.get("fcm_token")
        app_current_version = request.data.get("app_current_version")  

        if not id_token_value:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #  Verify token with Google — only your Web Client ID is needed
            idinfo = id_token.verify_oauth2_token(
                id_token_value,
                requests.Request(),
                settings.GOOGLE_WEB_CLIENT_ID,  # <— use Web Client ID only
            )

            # Ensure it's issued by Google
            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                return Response({"error": "Invalid issuer"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract user info
            email = idinfo.get("email")
            name = idinfo.get("name", "")
            picture = idinfo.get("picture", "")



          
            if not email:
                return Response({"error": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)

            #  Create or fetch user
            customer, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]},
            )


            customer_data = {} 

            if TermsAndConditionsAccept.objects.filter(user=customer).exists():
                customer_data['termsAccepted']=True
            else:
                customer_data['termsAccepted']=False

            # Update name fields for new users
            if created:
                parts = name.split()
                customer.first_name = parts[0] if parts else ""
                customer.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
                customer.save()
                customer_profile= Customer_profile.objects.create(customer=customer, profile_picture=picture)


            customer_data["new_user"] = created

            customer_profile= Customer_profile.objects.filter(customer=customer).first()
            serialized = CustomerProfileSerializer(customer_profile)
            

            if app_current_version:
                UserCurrentAppVersion.objects.update_or_create(
                    user=request.user,
                    defaults={"app_version": app_current_version}
                )

            if fcm_token:
                if not DeviceFCM.objects.filter(fcm_token=fcm_token).exists():
                    DeviceFCM.objects.update_or_create(
                        user=customer,
                        defaults={"fcm_token": fcm_token}
                    )

            #  Generate JWT tokens
            refresh = RefreshToken.for_user(customer)

            return Response(
                {
                    **serialized.data,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    **customer_data
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Token invalid or expired
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other errors
            return Response({"error": "Authentication failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)