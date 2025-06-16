from rest_framework import generics
from .models import AdminUser
from .serializers import AdminUserRegistrationSerializer

class AdminUserRegisterView(generics.CreateAPIView):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserRegistrationSerializer
