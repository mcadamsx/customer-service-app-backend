from rest_framework import serializers
from AdminAccounts.models import CustomerInvitationToken


class CustomerInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvitationToken
        fields = ['full_name', 'email', 'phone', 'company_name']

    def create(self, validated_data):
        admin = self.context['request'].user
        return CustomerInvitationToken.objects.create(
            admin=admin,
            **validated_data
        )
