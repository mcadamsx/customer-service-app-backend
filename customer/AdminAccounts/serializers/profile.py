from rest_framework import serializers
from ..models import AdminUser


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = [
            'company_name', 'company_email', 'address1',
            'region', 'country', 'phone', 'profile_photo',
            'company_description',
        ]
        read_only_fields = ['company_email']
