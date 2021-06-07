from django_filters import rest_framework as filters
from .models import *


class TimetableFilter(filters.FilterSet):
    service = filters.NumberFilter(field_name='service_field', method='filter_service')

    def filter_service(self, queryset, name, value):

        try:
            service = Service.objects.get(pk=value)
            return queryset.filter(service=service)
        except Service.DoesNotExist:
            return queryset.none()

    class Meta:
        model = TimeTable
        fields = [
            'service'
        ]
