from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict
from calendar import month_name

from ..models import Customer, Ticket, SubAdmin, Payment


def calc_percent_change(current, previous):
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        try:
            selected_year = int(request.query_params.get("year", now.year))
        except ValueError:
            selected_year = now.year

        start_of_year = now.replace(year=selected_year, month=1, day=1, hour=0, minute=0, second=0)
        end_of_year = now.replace(year=selected_year, month=12, day=31, hour=23, minute=59, second=59)

        verified_current = Customer.objects.filter(is_verified=True).count()
        verified_previous = Customer.objects.filter(
            is_verified=True,
            date_joined__range=(sixty_days_ago, thirty_days_ago)
        ).count()
        verified_percent = calc_percent_change(verified_current, verified_previous)

        new_current = Customer.objects.filter(date_joined__gte=thirty_days_ago).count()
        new_previous = Customer.objects.filter(
            date_joined__range=(sixty_days_ago, thirty_days_ago)
        ).count()
        new_percent = calc_percent_change(new_current, new_previous)

        open_current = Ticket.objects.filter(status='open').count()
        open_previous = Ticket.objects.filter(
            status='open',
            created_at__range=(sixty_days_ago, thirty_days_ago)
        ).count()
        open_percent = calc_percent_change(open_current, open_previous)

        subadmins_current = SubAdmin.objects.filter(is_active=True).count()
        subadmins_previous = SubAdmin.objects.filter(
            is_active=True,
            created_at__range=(sixty_days_ago, thirty_days_ago)
        ).count()
        subadmins_percent = calc_percent_change(subadmins_current, subadmins_previous)

        # ---------- Section 2: Revenue Chart Data ----------
        revenue_qs = (
            Payment.objects.filter(created_at__range=(start_of_year, end_of_year))
            .annotate(month=TruncMonth('created_at'))
            .values('month', 'service__name')
            .annotate(total=Sum('amount'))
            .order_by('month')
)

        revenue_data = defaultdict(lambda: [0] * 12)
        for entry in revenue_qs:
            service = entry['service__name'] or 'Unknown'
            month_index = entry['month'].month - 1
            revenue_data[service][month_index] = float(entry['total'])

        revenue_chart_data = []
        for i in range(12):
            row = {'name': month_name[i + 1][:3]}
            for service, monthly_totals in revenue_data.items():
                row[service] = monthly_totals[i]
            revenue_chart_data.append(row)

        monthly_customers = Customer.objects.filter(date_joined__year=selected_year) \
            .annotate(month=TruncMonth('date_joined')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        customer_counts = [0] * 12
        for entry in monthly_customers:
            index = entry['month'].month - 1
            customer_counts[index] = entry['count']

        customer_activity = {
            "months": [month_name[i][:3] for i in range(1, 13)],
            "counts": customer_counts
        }

        # ---------- Section 4: Top Locations ----------
        total_customers = Customer.objects.count()
        location_qs = Customer.objects.values('location') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:5]

        top_locations = []
        for entry in location_qs:
            percent = (entry['count'] / total_customers) * 100 if total_customers > 0 else 0
            top_locations.append({
                "country": entry['location'],
                "percentage": round(percent, 2)
            })

        return Response({
            "stats": {
                "verified_customers": {
                    "count": verified_current,
                    "percent_change": verified_percent
                },
                "new_customers": {
                    "count": new_current,
                    "percent_change": new_percent
                },
                "open_tickets": {
                    "count": open_current,
                    "percent_change": open_percent
                },
                "sub_admins": {
                    "count": subadmins_current,
                    "percent_change": subadmins_percent
                }
            },
            "revenue_chart_data": revenue_chart_data,
            "customer_activity": customer_activity,
            "top_locations": top_locations
        })
