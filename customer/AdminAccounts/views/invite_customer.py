from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from ..serializers import CustomerInvitationSerializer


class InviteCustomerView(APIView):
    """
    Admin invites a customer via email with a registration token link.
    """

    def post(self, request):
        serializer = CustomerInvitationSerializer(data=request.data)

        if serializer.is_valid():
            invitation = serializer.save()

            # Build token registration link
            registration_link = f"https://your-admin.com/customer/register/{invitation.token}"

            # Send email
            send_mail(
                subject="You're invited to register",
                message=(
                    f"Hello {invitation.full_name},\n\n"
                    f"You have been invited to register with {invitation.company_name}.\n"
                    f"Click the link below to complete your registration:\n{registration_link}\n\n"
                    f"This link will expire in 24 hours."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                fail_silently=False,
            )

            return Response({"message": "Invitation sent successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
