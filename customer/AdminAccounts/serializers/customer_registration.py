from rest_framework import serializers
from AdminAccounts.models import CustomerUser, CustomerInvitationToken
from AdminAccounts.models import CustomerEmailVerificationToken
from django.conf import settings
from django.core.mail import send_mail


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True, max_length=12)
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomerUser
        fields = [
            'full_name', 'email', 'phone', 'address1', 'address2',
            'region', 'country', 'password', 'repeat_password', 'token'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            token_obj = CustomerInvitationToken.objects.get(
                token=attrs['token'], used=False)
        except CustomerInvitationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or used token.")

        if token_obj.is_expired():
            raise serializers.ValidationError("Invitation token has expired.")

        if token_obj.email.lower() != attrs['email'].lower():
            raise serializers.ValidationError(
                "Email does not match the token."
            )

        attrs["token_obj"] = token_obj
        return attrs

    def create(self, validated_data):  # <-- make sure this is indented inside the class
        password = validated_data.pop("password")
        validated_data.pop("repeat_password", None)
        token_obj = validated_data.pop("token_obj", None)
        validated_data.pop("token", None)

        user = CustomerUser.objects.create_user(
            full_name=validated_data.get("full_name"),
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            address1=validated_data.get("address1"),
            address2=validated_data.get("address2"),
            region=validated_data.get("region"),
            country=validated_data.get("country"),
            # invited_by=token_obj.invited_by,
            invited_by=token_obj.admin,
            password=password
        )

        token_obj.used = True
        token_obj.save()

        token = CustomerEmailVerificationToken.generate_token()
        CustomerEmailVerificationToken.objects.create(user=user, token=token)

        verification_url = f"https://yourdomain.com/api/admin/verify-customer/?token={token}"
        send_mail(
            subject="Verify Your Email",
            message=(
                f"Hi {user.full_name},\n\n"
                f"Please verify your email by clicking the link below:\n{verification_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user
