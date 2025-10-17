from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests


User = get_user_model()

class Google_Signup(APIView):
   

   def post(self, request):
        id_token_value = request.data.get("id_token")
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
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]},
            )

            # Update name fields for new users
            if created:
                parts = name.split()
                user.first_name = parts[0] if parts else ""
                user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
                user.save()

            #  Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "picture": picture,
                    },
                    "new_user": created,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Token invalid or expired
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other errors
            return Response({"error": "Authentication failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)