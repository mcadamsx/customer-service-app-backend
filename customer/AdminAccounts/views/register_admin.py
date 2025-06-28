from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import timedelta
from AdminAccounts.models import AdminUser

from ..models import PasswordResetToken
from AdminAccounts.serializers.auth import (
    AdminRegisterSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)

User = get_user_model()


class RegisterAdminUserView(APIView):
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin registered successfully."},
                            status=201)
        return Response(serializer.errors, status=400)


class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get("company_email")
        password = request.data.get("password")
        remember_me = request.data.get("remember_me", False)

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = AdminUser.objects.get(company_email=email)
            if not user.check_password(password):
                raise AdminUser.DoesNotExist
        except AdminUser.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        access_expiry = (
            timedelta(days=20) if remember_me else timedelta(minutes=5))
        access.set_exp(lifetime=access_expiry)
        refresh.set_exp(lifetime=timedelta(days=20))  # Optional

        return Response({
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "expires_in": access_expiry.total_seconds(),
            "company_email": user.company_email,
            "company_name": user.company_name
        })


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "A reset password link has been sent to your email."
        })


class ResetPasswordView(APIView):
    def post(self, request, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token_obj = (
                    PasswordResetToken.objects.get(token=token, is_used=False))
            except PasswordResetToken.DoesNotExist:
                return Response({"detail": "Invalid or already used "
                                "reset token."}, status=400)

            if token_obj.is_expired():
                return Response({"detail": "Reset token has expired."},
                                status=400)

            user = token_obj.user
            new_password = serializer.validated_data['new_password']

            user.set_password(new_password)
            user.save()

            token_obj.is_used = True
            token_obj.save()

            return Response({"detail": "Password reset successful."})
        return Response(serializer.errors, status=400)
