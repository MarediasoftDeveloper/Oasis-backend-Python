from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.DeviceFcmToken import DeviceFCM



class SaveFCMToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("fcm_token")
        if not DeviceFCM.objects.filter(fcm_token=token).exists():    
            return Response({"message": "Token exits!"})
        
        DeviceFCM.objects.update_or_create(
            user=request.user,
            defaults={"fcm_token": token}
        )

        return Response({"message": "Token saved"})
