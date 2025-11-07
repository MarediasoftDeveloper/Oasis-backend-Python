from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Customer
from rest_framework_simplejwt.tokens import RefreshToken

class Logout(APIView):

    def post(self, request):

        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message":"Logged out successfully!"})

        except Exception as e:
            return Response({"error":f"An Error occured: {e}"}, status=400)
