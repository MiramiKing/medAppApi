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


class ServiceMedPersonaFilter(filters.FilterSet):
    service_type = filters.ChoiceFilter(
        field_name='service_type',
        choices=SERVICE_CHOICES,
        method='filter_service_type'
    );

    def filter_service_type(self, queryset, name, value):
        service_queryset = None

        if value == 'Procedure':
            service_queryset = Procedure.objects.all()
        elif value == 'Event':
            service_queryset = Event.objects.all()
        elif value == 'Survey':
            service_queryset = Survey.objects.all()
        elif value == 'Speciality':
            service_queryset = Speciality.objects.all()

        try:
            service_id_list = service_queryset.values_list('service__id', flat=True)
        except:
            return queryset.none()
        else:
            return queryset.filter(service__id__in=service_id_list)

    class Meta:
        model = ServiceMedPersona
        fields = [
            'service_type',
        ]


class ServiceFilter(filters.FilterSet):
    service_type = filters.ChoiceFilter(
        field_name='service_type',
        choices=SERVICE_CHOICES,
        method='filter_service_type'
    );

    def filter_service_type(self, queryset, name, value):
        service_queryset = None

        if value == 'Procedure':
            service_queryset = Procedure.objects.all()
        elif value == 'Event':
            service_queryset = Event.objects.all()
        elif value == 'Survey':
            service_queryset = Survey.objects.all()
        elif value == 'Speciality':
            service_queryset = Speciality.objects.all()

        try:
            service_id_list = service_queryset.values_list('service__id', flat=True)
        except:
            return queryset.none()
        else:
            return queryset.filter(id__in=service_id_list)

    class Meta:
        model = Service
        fields = [
            'service_type',
        ]
