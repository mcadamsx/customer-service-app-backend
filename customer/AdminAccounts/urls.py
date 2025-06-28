from django.urls import path
from .views.invite_admin import InviteAdminUserView
from .views.register_admin import RegisterAdminUserView
from .views.register_admin import (
    AdminLoginView,
    ForgotPasswordView,
    ResetPasswordView,
)
from .views.dashboard import AdminDashboardView
from .views.profile import AdminProfileUpdateView


urlpatterns = [
    path('invite/', InviteAdminUserView.as_view(), name='invite-admin'),
    path('register/', RegisterAdminUserView.as_view(), name='register-admin'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('forgot-password/', ForgotPasswordView.as_view(),
         name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(),
         name='reset-password'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('profile/', AdminProfileUpdateView.as_view(),
         name='admin-profile'),


]
