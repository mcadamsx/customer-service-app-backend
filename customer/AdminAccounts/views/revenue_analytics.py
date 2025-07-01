from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum
from AdminAccounts.models import Payment


def calc_percent_change(current, previous):
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def revenue_analytics(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Total revenue last 30 days
    total_current = Payment.objects.filter(
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total revenue previous 30 days
    total_previous = Payment.objects.filter(
        created_at__range=(sixty_days_ago, thirty_days_ago)
    ).aggregate(total=Sum('amount'))['total'] or 0

    percent_change = calc_percent_change(total_current, total_previous)

    # Revenue per service
    revenue_per_service = Payment.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('service__name').annotate(
        total=Sum('amount')
    )

    return Response({
        "total_revenue": total_current,
        "revenue_growth_percent": percent_change,
        "revenue_per_service": revenue_per_service
    })
