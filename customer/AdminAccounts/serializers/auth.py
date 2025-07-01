from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from ..models import PasswordResetToken
from AdminAccounts.models import AdminUser, AdminSignupToken


class AdminRegisterSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=12)
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = [
            'company_name', 'company_email', 'address1', 'address2', 'region',
            'country', 'phone', 'password', 'repeat_password', 'token'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            token_obj = AdminSignupToken.objects.get(token=attrs['token'],
                                                     used=False)
        except AdminSignupToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used token.")

        if token_obj.is_expired():
            raise serializers.ValidationError("Token has expired.")

        if token_obj.email.lower() != attrs['company_email'].lower():
            raise serializers.ValidationError("Email does not match the "
                                              "invitation token.")

        attrs["token_obj"] = token_obj
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("repeat_password")
        token_obj = validated_data.pop("token_obj")
        validated_data.pop("token")

        user = AdminUser.objects.create_user(
            password=password,
            **validated_data
        )
        token_obj.used = True
        token_obj.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not AdminUser.objects.filter(company_email=value).exists():
            raise serializers.ValidationError("Admin with this "
                                              "email not found.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = AdminUser.objects.get(company_email=email)
        token_obj = PasswordResetToken.objects.create(user=user)
        reset_url = (
            f"http://localhost:8000/reset-password?token={token_obj.token}")

        send_mail(
            "Password Reset Request",

            f"Hi {user.company_name},\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n"
            f"This link will expire in 1 hour.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        return token_obj


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
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
