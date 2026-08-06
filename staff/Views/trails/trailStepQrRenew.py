# from rest_framework import APIView, status
# from rest_framework.response import Response
# from app.Models.trails.trailModel import Trail 
# from app.Models.trails.trailRecord import TrailRecord 
# from app.Models.trails.trailSteps import TrailStep
# from app.Serializers.trailSerializers.trail_serializers import TrailSerializer 
# from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializerStaff 
# from rest_framework.permissions import IsAuthenticated
# from staff.Permissions.admin_only_permission import Request_By_Admin_Only
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from venue.models.qr_info_model import QR_Info


# class TrailStepsQRRenew(APIView):
#     permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    
    
#     def post(self, request):
#         trail_step_id = request.data.get('trail_step_id')

#         if trail_step_id is not None:
#             trail_step = TrailStep.objects.filter(id=trail_step_id).first()
#             new_qr = QR_Info()
#             new_qr.save()
#             trail_step.qr_code = new_qr
#             trail_step.save()
#             return Response({
#                 "message": "QR code renewed successfully."
#             })

  

