from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from AdminAccounts.models import CustomerInvitationToken, AdminUser


class InviteCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.user, AdminUser):
            return Response({"error": "Only admins can invite customers."}, status=403)

        email = request.data.get("email")
        full_name = request.data.get("full_name")
        phone = request.data.get("phone", "")
        company_name = request.data.get("company_name")

        if not all([email, full_name, company_name]):
            return Response({"error": "Email, full_name, and company_name are required."}, status=400)

        token_obj = CustomerInvitationToken.objects.create(
            admin=request.user,
            invited_by=request.user,
            email=email,
            full_name=full_name,
            phone=phone,
            company_name=company_name
        )

        signup_link = f"http://localhost:8000/register-customer?token={token_obj.token}"

        send_mail(
            subject="Customer Registration Invite",
            message=f"Hi {full_name},\n\nClick the link to register: {signup_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        # ✅ Print to console
        print(f"Invitation sent to {email}. Token: {token_obj.token}")

        return Response({"message": f"Signup link sent to {email}."}, status=200)
