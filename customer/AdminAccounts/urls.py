from django.urls import path
from .views import AdminUserRegisterView

urlpatterns = [
    path('register/', AdminUserRegisterView.as_view(), name='admin-register'),
]
