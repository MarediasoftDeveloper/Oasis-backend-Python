from rest_framework import generics
from app.Permissions.write_by_customer_only_where_obj_user import WriteByCustomerOnlyUser
from app.Serializers.termsAndConditionSerializer import TermsAndConditionsSerializer
from rest_framework.response import Response
from app.Models.terms_and_conditions_accept import TermsAndConditionsAccept
from rest_framework.permissions import IsAuthenticated


class TermsAndConditionsAcceptView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset=TermsAndConditionsAccept.objects.all()
    serializer_class=TermsAndConditionsSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)