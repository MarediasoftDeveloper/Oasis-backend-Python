from django.shortcuts import render
from rest_framework import generics 
from app.Models.customers import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer 
# Create your views here.

class Update_Customer(generics.UpdateAPIView):

    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer
    

