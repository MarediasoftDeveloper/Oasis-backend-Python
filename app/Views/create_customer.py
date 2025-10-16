from django.shortcuts import render, redirect
from rest_framework import generics 
from app.models import Customer
from app.Serializers.customer_signup_serializer import Customer_Serializer 
from rest_framework import status
import random



class Create_Customer(generics.CreateAPIView):

    queryset = Customer.objects.all()
    serializer_class = Customer_Serializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            customer_id = response.data.get('id')
            return redirect('send-and-validate-otp', customer_id)


        return response
