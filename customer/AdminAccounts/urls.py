from django.urls import path
from .views.invite_admin import InviteAdminUserView
from .views.register_admin import RegisterAdminUserView
from .views.register_admin import (
    AdminLoginView,
    ForgotPasswordView,
    ResetPasswordView,
)
from AdminAccounts.views import dashboard
from AdminAccounts.views.revenue_analytics import revenue_analytics
from AdminAccounts.views.customer_activity import customer_activity_over_time
from AdminAccounts.views.top_customers_locations import top_customer_locations


urlpatterns = [
    path('invite/', InviteAdminUserView.as_view(), name='invite-admin'),
    path('register/', RegisterAdminUserView.as_view(), name='register-admin'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('forgot-password/', ForgotPasswordView.as_view(),
         name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(),
         name='reset-password'),
    path('dashboard-summary/', dashboard.dashboard_summary),
    path('revenue-analytics/', revenue_analytics, name='revenue-analytics'),
    path('customer-activity/', customer_activity_over_time,
         name='customer-activity'),
    path('customer-locations/', top_customer_locations,
         name='top-customer-locations'),


]
