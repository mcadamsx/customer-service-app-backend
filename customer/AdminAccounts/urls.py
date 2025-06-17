from django.urls import path
from .views.auth import AdminUserRegisterView, VerifyAdminEmailView
from .views.auth import AdminLoginView
from .views.auth import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', AdminUserRegisterView.as_view(), name='admin-register'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('verify-email/<str:token>/', VerifyAdminEmailView.as_view(), name='admin-verify-email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    
    
]
