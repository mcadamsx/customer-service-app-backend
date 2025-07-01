from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count

from AdminAccounts.models import Customer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def top_customer_locations(request):
    """
    Returns the number of customers grouped by location.
    """
    queryset = (
        Customer.objects
        .values('location')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return Response({
        "locations": list(queryset)
    })
