import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from app.models import Customer_profile
from app.Models.DeviceFcmToken import DeviceFCM
from app.Models.terms_and_conditions_accept import TermsAndConditionsAccept
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Models.user_current_app_version import UserCurrentAppVersion

User = get_user_model()


class Facebook_Signup(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token")
        fcm_token = request.data.get("fcm_token")
        app_current_version = request.data.get("app_current_version")


        if not access_token:
            # something went wrong! please try again.
            return Response(
                {"error": "something went wrong! please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1️⃣ Verify token & get user info from Facebook
            user_info_url = "https://graph.facebook.com/me"
            params = {
                "fields": "id,name,email",
                "access_token": access_token,
            }

            fb_response = requests.get(user_info_url, params=params)
            fb_data = fb_response.json()

            if "error" in fb_data:
                # invalid token 
                return Response(
                    {"error": "something went wrong! please try again.", "details": fb_data},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = fb_data.get("email")
            name = fb_data.get("name", "")
           
            if not email:
                # email permission not granted from facebook 
                return Response(
                    {"error": "something went wrong! please try again."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2️⃣ Create or get user
            customer, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]},
                is_google_or_apple_account=True
            )

            customer_data = {}

            if TermsAndConditionsAccept.objects.filter(user=customer).exists():
                customer_data["termsAccepted"] = True
            else:
                customer_data["termsAccepted"] = False

            # 3️⃣ Update new user data
            if created:
                parts = name.split()
                customer.first_name = parts[0] if parts else ""
                customer.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
                customer.is_verified = True
                customer.save()

                Customer_profile.objects.create(
                    customer=customer
                )

            customer_data["new_user"] = created

            customer_profile = Customer_profile.objects.filter(customer=customer).first()
            serialized = CustomerProfileSerializer(customer_profile)

            if not customer.is_google_or_apple_account:
                 return Response(
                    {"error": "Account with this email already exists, please login by using email and password!"},
                    status=status.HTTP_401_UNAUTHORIZED
                )


            # 4️⃣ Save app version
            if app_current_version:
                UserCurrentAppVersion.objects.update_or_create(
                    user=customer,
                    defaults={"app_version": app_current_version}
                )

            # 5️⃣ Save FCM token
            if fcm_token:
                DeviceFCM.objects.update_or_create(
                    user=customer,
                    defaults={"fcm_token": fcm_token}
                )

            # 6️⃣ Generate JWT tokens
            refresh = RefreshToken.for_user(customer)

            return Response(
                {
                    **serialized.data,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    **customer_data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Facebook authentication failed 
            return Response(
                {"error": "something went wrong! please try again.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
