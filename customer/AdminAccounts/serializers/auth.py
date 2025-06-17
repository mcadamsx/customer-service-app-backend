from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from ..models import AdminUser, PasswordResetToken


class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repeat_password = serializers.CharField(write_only =True)

    class Meta:
        model = AdminUser
        fields = [
            'company_name', 'company_email', 'password', 'repeat_password',
            'address1', 'address2', 'region', 'country', 'phone', 'registration_token'
        ]
        
        def validate(self, attrs):
            if attrs['password'] != attrs['repeat_password']:
                raise serializers.ValidationError({"password": "Passwords don't match."})
            return attrs
        read_only_fields = ['registration_token']

    def create(self, validated_data):
        validated_data.pop("repeat_password")
        user = AdminUser.objects.create_user(**validated_data)
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not AdminUser.objects.filter(company_email=value).exists():
            raise serializers.ValidationError("Admin with this email not found.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = AdminUser.objects.get(company_email=email)
        token_obj = PasswordResetToken.objects.create(user=user)
        reset_url =  f"http://localhost:8000/api/admin/reset-password/{token_obj.token}/"

        send_mail(
            "Password Reset Request",
            f"Hi {user.company_name},\nClick the link below to reset your password:\n\n{reset_url}\n\nThis link will expire in 30 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        return token_obj


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            token_obj = PasswordResetToken.objects.get(token=data['token'], is_used=False)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used reset token.")

        if token_obj.is_expired():
            raise serializers.ValidationError("Reset token has expired.")

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        data['user'] = token_obj.user
        data['token_obj'] = token_obj
        return data

    def save(self):
        user = self.validated_data['user']
        token_obj = self.validated_data['token_obj']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        token_obj.is_used = True
        token_obj.save()

        return user
