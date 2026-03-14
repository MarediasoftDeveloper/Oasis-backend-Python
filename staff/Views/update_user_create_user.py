
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from staff.Serializers.customer_serializer_staff import Customer_Serializer_Staff
from app.models import Customer



class AdminUserListCreateUpdateDelete(ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = Customer_Serializer_Staff
    
    def get_queryset(self):
        return Customer.objects.filter(user_role__in=['3','4'])
   


class AdminDetails(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def get(self, request):
        customer= Customer.objects.filter(id=request.user.id, user_role='3').first()
        admin_data = Customer_Serializer_Staff(customer)
        return Response({"admin_data":admin_data.data})
    



class AdminPasswordReset(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
       

        if not email or not password:
            return Response(
                {"message": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = Customer.objects.filter(email__iexact=email).first()
        if not customer:
            return Response(
                {"message": "User does not exist with this email."},
                status=status.HTTP_404_NOT_FOUND
            )

        customer.set_password(password)
        customer.save()  # THIS IS REQUIRED

        return Response(
            {"message": f"Password successfully updated for {customer.username}"},
            status=status.HTTP_200_OK
        )