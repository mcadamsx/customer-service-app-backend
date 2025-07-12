from django.urls import path
from .views.invite_admin import InviteAdminUserView
from .views.register_admin import (
    RegisterAdminUserView,
    AdminLoginView,
    ForgotPasswordView,
    ResetPasswordView,
)
from .views.dashboard import AdminDashboardView
from .views.invite_customer import InviteCustomerView
from .views.customer_registration import CustomerRegistrationView
from .views.customer_registration import CustomerEmailVerificationView
from .views.register_admin import AdminEmailVerificationView

urlpatterns = [
     path('invite/', InviteAdminUserView.as_view(), name='invite-admin'),
     path('register/', RegisterAdminUserView.as_view(), name='register-admin'),
     path('verify-admin/', AdminEmailVerificationView.as_view(), name="admin-verify-email"),

     path('login/', AdminLoginView.as_view(), name='admin_login'),
     path('forgot-password/', ForgotPasswordView.as_view(),
          name='forgot-password'),
     path('reset-password/<str:token>/', ResetPasswordView.as_view(),
          name='reset-password'),
     path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
     path('invite-customer/', InviteCustomerView.as_view(),
          name='invite-customer'),
     path('register-customer/', CustomerRegistrationView.as_view(),
          name='customer-register'),
     path('verify-customer/', CustomerEmailVerificationView.as_view(),
          name='customer-verify-email'),
]
