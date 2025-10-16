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
    """
    Google Sign-In endpoint for both Android & iOS.
    POST { "id_token": "<google_id_token>" }
    """

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google's public keys
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=settings.GOOGLE_CLIENT_IDS
            )

            # Ensure the token is issued by Google accounts
            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Invalid issuer.")

            email = idinfo.get("email")
            name = idinfo.get("name", "")
            picture = idinfo.get("picture", "")

            if not email:
                return Response({"error": "Email not found in token"}, status=400)

            # Create or update user
            user, created = User.objects.get_or_create(email=email, defaults={"username": email})
            if created:
                user.first_name = name.split()[0] if name else ""
                user.last_name = " ".join(name.split()[1:]) if len(name.split()) > 1 else ""
                user.save()

            # Generate JWT tokens
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
            return Response({"error": "Authentication failed", "details": str(e)}, status=400)
