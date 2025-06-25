from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from AdminAccounts.models import AdminSignupToken


class InviteAdminUserView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=400)

        # Create token
        token_obj = AdminSignupToken.objects.create(email=email)

        # You can build a frontend route like /register?token=xxx
        signup_link = f"http://localhost:8000/register?token={token_obj.token}"

        send_mail(
            subject="Admin Registration Invite",
            message=f"Click the link to register: {signup_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": f"Signup link sent to {email}."},
                        status=200)
