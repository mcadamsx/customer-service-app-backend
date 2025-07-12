from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.customer_registration import CustomerRegistrationSerializer
from ..models import CustomerEmailVerificationToken


class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": (
                        "Registration successful. Please check your email to "
                        "verify your account."
                    )
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerEmailVerificationView(APIView):
    def get(self, request):
        token = request.GET.get('token')

        if not token:
            return Response(
                {"detail": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_obj = CustomerEmailVerificationToken.objects.get(token=token)
        except CustomerEmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user

        if user.is_verified:
            return Response(
                {"detail": "Account already verified."},
                status=status.HTTP_200_OK
            )

        user.is_active = True
        user.is_verified = True
        user.save()

        token_obj.delete()

        return Response(
            {"detail": "Email successfully verified."},
            status=status.HTTP_200_OK
        )
