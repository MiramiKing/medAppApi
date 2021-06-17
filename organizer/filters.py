from django_filters import rest_framework as filters
from organizer.models import *
from med.models import SERVICE_CHOICES, Procedure, Event, Survey, Speciality, Service

class RecordFilter(filters.FilterSet):
    date_start__gte = filters.IsoDateTimeFilter(field_name='date_start', lookup_expr='gte')
    date_end__lte = filters.IsoDateTimeFilter(field_name='date_end', lookup_expr='lte')
    service_type = filters.ChoiceFilter(field_name='service_type', choices=SERVICE_CHOICES, method='filter_service_type')

    def filter_service_type(self, queryset, name, value):
        service_queryset = queryset.none()

        if value == 'Procedure':
            service_queryset = Procedure.objects.all()
        elif value == 'Event':
            service_queryset = Event.objects.all()
        elif value == 'Survey':
            service_queryset = Survey.objects.all()
        elif value == 'Speciality':
            service_queryset = Speciality.objects.all()

        service_id_list = service_queryset.values_list('service__id', flat=True)
        record_services = RecordService.objects.filter(service__id__in=service_id_list)
        record_id_list = record_services.values_list('record__id', flat=True)
        return queryset.filter(id__in=record_id_list)

    class Meta:
        model = Record
        fields = [
            'date_start',
            'date_end',
            'service_type',
        ]


class RecordServiceFilter(filters.FilterSet):
    service_type = filters.ChoiceFilter(field_name='service_type', choices=SERVICE_CHOICES, method='filter_service_type')

    def filter_service_type(self, queryset, name, value):
        service_queryset = queryset.none()

        if value == 'Procedure':
            service_queryset = Procedure.objects.all()
        elif value == 'Event':
            service_queryset = Event.objects.all()
        elif value == 'Survey':
            service_queryset = Survey.objects.all()
        elif value == 'Speciality':
            service_queryset = Speciality.objects.all()

        service_id_list = service_queryset.values_list('service__id', flat=True)
        return queryset.filter(service__id__in=service_id_list)

    class Meta:
        model = RecordService
        fields = ['service_type']

