from django.shortcuts import render
from rest_framework import generics 
from app.models import Customer_profile
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Permissions.write_by_customer_only import WriteByCustomerOnly
from rest_framework.permissions import IsAuthenticated

class Update_Customer_Info(generics.RetrieveUpdateDestroyAPIView):

    permission_classes=[IsAuthenticated, WriteByCustomerOnly]
    queryset = Customer_profile.objects.all()
    serializer_class = CustomerProfileSerializer
    lookup_field = 'customer'
