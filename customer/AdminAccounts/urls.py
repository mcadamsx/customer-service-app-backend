from django.urls import path
from .views import AdminUserRegisterView, VerifyAdminEmailView
from .views import AdminLoginView

urlpatterns = [
    path('register/', AdminUserRegisterView.as_view(), name='admin-register'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('verify-email/<str:token>/', VerifyAdminEmailView.as_view(), name='admin-verify-email'),
    
]
