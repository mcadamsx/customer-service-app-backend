from rest_framework import serializers
from AdminAccounts.models import CustomerInvitationToken


class CustomerInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvitationToken
        fields = ['full_name', 'email', 'phone', 'company_name']
