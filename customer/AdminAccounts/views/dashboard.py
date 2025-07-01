from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from AdminAccounts.models import Customer, Ticket, SubAdmin


def calc_percent_change(current, previous):
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    verified_current = Customer.objects.filter(is_verified=True).count()
    verified_previous = Customer.objects.filter(
        is_verified=True,
        date_joined__range=(sixty_days_ago, thirty_days_ago)
    ).count()
    verified_percent = calc_percent_change(verified_current, verified_previous)

    new_current = Customer.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
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
    subadmins_percent = (
        calc_percent_change(subadmins_current, subadmins_previous))

    return Response({
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
    })
