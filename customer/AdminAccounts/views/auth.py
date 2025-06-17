from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import timedelta
from ..models import AdminUser, PasswordResetToken
from AdminAccounts.serializers.auth import (
    AdminUserRegistrationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
User = get_user_model()


# -------------------------------
# Registration & Email Verification
# -------------------------------
class AdminUserRegisterView(generics.CreateAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_verification_email(user)

    def send_verification_email(self, user):
        token = user.registration_token
        verification_link = f"http://localhost:8000/api/admin/verify-email/{token}/"
        subject = "Verify your Admin Account"
        message = f"Hi {user.company_name},\n\nPlease verify your admin account by clicking the link below:\n{verification_link}\n\nThank you!"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.company_email])


class VerifyAdminEmailView(APIView):
    def get(self, request, token):
        try:
            user = AdminUser.objects.get(registration_token=token)
            if user.is_verified:
                return Response({"message": "Account already verified"}, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        except AdminUser.DoesNotExist:
            return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Login View
# -------------------------------
class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get("company_email")
        password = request.data.get("password")
        remember_me = request.data.get("remember_me", False)

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        access_expiry = timedelta(days=20) if remember_me else timedelta(minutes=5)
        access.set_exp(lifetime=access_expiry)
        refresh.set_exp(lifetime=timedelta(days=20))  # optional

        return Response({
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "expires_in": access_expiry.total_seconds(),
            "company_email": user.company_email,
            "company_name": user.company_name
        })


# -------------------------------
# Password Reset Flow
# -------------------------------
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Handles sending email internally
        return Response({"message": "A reset password link has been sent to your email."})


class ResetPasswordView(APIView):
    def post(self, request, token):
        try:
            token_obj = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid or already used token."}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data={**request.data, "token": token})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
