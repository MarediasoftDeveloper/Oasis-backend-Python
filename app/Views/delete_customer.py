from django.shortcuts import render
from rest_framework import generics 
from app.models import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer 
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Permissions.write_by_customer_only import WriteByCustomerOnly



class Delete_Customer(generics.DestroyAPIView):

    permission_classes=[IsAuthenticated, WriteByCustomerOnly]
    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer