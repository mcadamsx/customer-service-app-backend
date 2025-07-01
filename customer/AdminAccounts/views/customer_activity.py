from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from django.db.models import Count

from AdminAccounts.models import Customer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def customer_activity_over_time(request):
    """
    Returns the number of customers
    registered per month over the last 12 months.
    """
    now = timezone.now()
    twelve_months_ago = now - timedelta(days=180)

    # Annotate customers grouped by month
    queryset = (
        Customer.objects
        .filter(date_joined__gte=twelve_months_ago)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = []
    data = []

    for entry in queryset:
        labels.append(entry['month'].strftime('%b %Y'))
        data.append(entry['count'])

    return Response({
        "labels": labels,
        "data": data
    })
