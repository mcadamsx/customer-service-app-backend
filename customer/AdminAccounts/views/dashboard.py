from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Count
from datetime import timedelta
from ..models import AdminUser
from django.db.models.functions import TruncMonth
from AdminAccounts.models import Customer, Ticket
from AdminAccounts.models import Service
from ..serializers.dashboard import AdminDashboardSerializer


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()
        one_week_ago = today - timedelta(days=7)
        current_year = today.year

        verified_customers = Customer.objects.filter(is_online=True).count()
        new_customers = (
            Customer.objects.filter(date_joined__gte=one_week_ago).count())
        open_tickets = (Ticket.objects.filter(status="open").count())
        sub_admin_count = (
            AdminUser.objects.filter(is_staff=True, is_superuser=False).count()
            )

        top_services = (
            Service.objects.annotate(customer_count=Count
                                     ('customers')).order_by
                                    ('-customer_count')[:5])
        top_services_list = [service.name for service in top_services]

        locations = (
            Customer.objects.values_list('location', flat=True).distinct())

        monthly_data = Customer.objects.filter(date_joined__year=current_year)\
            .annotate(month=TruncMonth('date_joined')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')
        yearly_activity = {item['month'].strftime("%B"): item['count']
                           for item in monthly_data}

        dashboard_data = {
            "verified_customers": verified_customers,
            "new_customers": new_customers,
            "open_tickets": open_tickets,
            "sub_admin_count": sub_admin_count,
            "top_services": top_services_list,
            "customer_locations": list(locations),
            "yearly_activity": yearly_activity
        }
        serializer = AdminDashboardSerializer(dashboard_data)
        return Response(serializer.data)
