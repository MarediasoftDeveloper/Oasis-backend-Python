from rest_framework.views import APIView
from rest_framework.response import Response
from app.Models.customers import Customer
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken



class Login(APIView):   

    def post(self, request):

        data = request.data.get('credentials')
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return Response({'error':"Credentials not provided!"})
        else:
            try:
                customer = Customer.objects.get(email=email)
                if customer:
                    authenticated_user = check_password(password, customer.password)
                    if authenticated_user:
                        refresh = RefreshToken.for_user(customer)
                        return Response({
                            'customer':
                                {
                                'id':customer.id,
                                'username': customer.username,
                                'email': customer.email,
                                },
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh),
                        })
                    else:
                        return Response({'error':'One or more information is incorrect!'})

                else:
                    return Response({'error':'One or more information is incorrect!'})

                
            except Exception as e:
                    return Response({'error':'One or more information is incorrect!'})



                        
                        
            


