from rest_framework import serializers
from .models import AdminUser

class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AdminUser
        fields = [
            'company_name', 'company_email', 'password',
            'address1', 'address2', 'street', 'town',
            'region', 'country', 'phone', 'registration_token'
        ]
        read_only_fields = ['registration_token']

    def create(self, validated_data):
        return AdminUser.objects.create_user(**validated_data)
