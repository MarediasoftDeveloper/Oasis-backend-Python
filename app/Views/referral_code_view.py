from rest_framework.views import APIView
from app.models import Customer
from app.Views.use_referral_code import UseReferralCode

from rest_framework.response import Response



class ReferrlCodeUseView(APIView):

    def get(self, request):
        
        id = request.data.get('customer_id')
        referral_code = request.data.get('referral_code')
        customer=Customer.objects.filter(id=id).first()
        response = UseReferralCode(customer, referral_code)

        Response(response)
        
        

