from rest_framework.views  import APIView 
from app.models import Customer
from venue.Serializers.venue_signup_serializer import Venue_SignUp_Serializer 
from rest_framework import status
from app.Views.email.send_and_validate_email import Send_Otp_Mail
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from venue.models.challenges import Challenges
from venue.models.qr_info_model import QR_Info
from app.Models.trails.trailModel import Trail

class Change_All_Old_QRs(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            challenges = Challenges.objects.all()
            for challenge in challenges:
                new_qr = QR_Info(qr_type=QR_Info.QRType.CHALLENGE, expires_at=challenge.qr_code.expires_at)
                new_qr.save()
                challenge.qr_code = new_qr
                challenge.save()
            return Response({"message": "All old QR codes have been changed successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Change_All_Trails_Old_QRs(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            trails = Trail.objects.all()
            for trail in trails:
                trail_steps = trail.steps.all()
                for step in trail_steps:
                    new_qr = QR_Info(qr_type=QR_Info.QRType.TRAIL, expires_at=step.qr_code.expires_at)
                    new_qr.save()
                    step.qr_code = new_qr
                    step.save()
            return Response({"message": "All old QR codes have been changed successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)