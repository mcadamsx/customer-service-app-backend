from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import AdminUserRegistrationSerializer
from django.core.mail import send_mail
from django .conf import settings
from django.http import JsonResponse
from .models import AdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta
from django.utils import timezone


class AdminUserRegisterView(generics.CreateAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserRegistrationSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        self.send_verification_email(user)
        
    def send_verification_email(self, user):
        token = user.registration_token
        verification_link = f"http://localhost:8000/api/admin/verify-email/{token}/"
        
        subject = "verify your Admin Account"
        message = f"Hi {user.company_name},\n\nPlease verify your admin account by clicking the link below:\n{verification_link}\n\nThank you!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.company_email]
        
        send_mail(subject, message, from_email, recipient_list)
        
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
    

class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get("company_email")
        password = request.data.get("password")
        remember_me = request.data.get("remember_me", False)

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Set token lifetime based on remember_me
        if remember_me:
            lifetime = timedelta(days=20)
        else:
            lifetime = timedelta(minutes=5)

        access.set_exp(lifetime=lifetime)
        refresh.set_exp(lifetime=timedelta(days=20))  # Optional

        return Response({
            "message": "Login successful",
            "access": str(access),
            "refresh": str(refresh),
            "expires_in": lifetime.total_seconds(),
            "company_email": user.company_email,
            "company_name": user.company_name
        }, status=status.HTTP_200_OK)