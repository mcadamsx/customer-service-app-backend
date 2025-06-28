from rest_framework import generics, permissions
from ..serializers.profile import AdminProfileSerializer


class AdminProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
