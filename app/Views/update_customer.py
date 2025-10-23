from django.shortcuts import render
from rest_framework import generics 
from app.models import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer 
from rest_framework.permissions import IsAuthenticated, AllowAny



class Update_Customer(generics.UpdateAPIView):

    permission_classes=[AllowAny]
    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer