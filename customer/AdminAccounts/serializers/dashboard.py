from rest_framework import serializers

class AdminDashboardSerializer(serializers.Serializer):
    verified_customers = serializers.IntegerField()
    new_customers = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    sub_admin_count = serializers.IntegerField()
    top_services = serializers.ListField(child=serializers.CharField())
    customer_locations = serializers.ListField(child=serializers.CharField())
    yearly_activity = serializers.DictField(child=serializers.IntegerField())