import hashlib
import jwt
import requests
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from app.apple import generate_apple_client_secret
from app.Models.DeviceFcmToken import DeviceFCM
from app.Models.user_current_app_version import UserCurrentAppVersion
from app.Models.terms_and_conditions_accept import TermsAndConditionsAccept
from app.models import Customer_profile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from django.db.models import Q
from jwt import PyJWKClient



User = get_user_model()

def generate_apple_username(apple_sub: str) -> str:
    digest = hashlib.sha256(apple_sub.encode()).hexdigest()
    return f"apple_{digest[:8]}"


class AppleLogin(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data 

        identity_token = data.get("identity_token")
        auth_code = data.get("authorization_code")
        full_name = data.get("full_name")  
        fcm_token = data.get("fcm_token")  
        app_current_version = data.get("app_current_version")  

        if not identity_token or not auth_code:
            return Response({"error": "Missing token"}, status=400)

        token_response = requests.post(
            "https://appleid.apple.com/auth/token",
            data={
                "client_id": settings.APPLE_CLIENT_ID,
                "client_secret": generate_apple_client_secret(),
                "code": auth_code,
                "grant_type": "authorization_code",
            },
        )

        token_data = token_response.json()
        if "error" in token_data:
            return Response(token_data, status=400)

        identity_token = token_data.get("id_token")

        # Verify Apple token
        jwks_client = PyJWKClient("https://appleid.apple.com/auth/keys")
        signing_key = jwks_client.get_signing_key_from_jwt(identity_token)

        decoded = jwt.decode(
            identity_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
            issuer="https://appleid.apple.com",
        )

        apple_sub = decoded["sub"]
        email = decoded.get("email") or f"{apple_sub}@appleid.apple"

 
        user = User.objects.filter(apple_sub=apple_sub).first()

        created = False
        
        customer_data={}
    

        if not user and email is not None:
            user = User.objects.create_user(
                username=generate_apple_username(apple_sub),
                email=email,
                apple_sub=apple_sub,
            )

            if full_name:
                parts = full_name.strip().split()
                user.first_name = parts[0] 
                user.last_name = " ".join(parts[1:])
                user.save()

            user.is_verified = True
            Customer_profile.objects.create(customer=user)
            created = True

        customer_data["new_user"] = created


        # Safe profile fetch
        customer_profile = Customer_profile.objects.filter(customer=user).first()
        serialized = CustomerProfileSerializer(customer_profile).data if customer_profile else {}
        # Terms check AFTER user exists
        terms_accepted = TermsAndConditionsAccept.objects.filter(user=user).exists()
        customer_data['termsAccepted'] = terms_accepted
        
        # Correct user reference
        if app_current_version:
            UserCurrentAppVersion.objects.update_or_create(
                user=user,
                defaults={"app_version": app_current_version}
            )

        if fcm_token:
            if not DeviceFCM.objects.filter(fcm_token=fcm_token).exists():
                DeviceFCM.objects.update_or_create(
                    user=user,
                    defaults={"fcm_token": fcm_token}
               )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
            **serialized,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            **customer_data
            },
            status=status.HTTP_200_OK,
        )
