from django_filters import rest_framework as filters
from organizer.models import *
from med.models import SERVICE_CHOICES, Procedure, Event, Survey, Speciality

class RecordFilter(filters.FilterSet):
    service_type = filters.ChoiceFilter(field_name='service_type', choices=SERVICE_CHOICES, method='filter_service_type')

    def filter_service_type(self, queryset, name, value):
        service_queryset = queryset.none()
        service_type = value.lower()

        if service_type == 'procedure':
            service_queryset = Procedure.objects.all()
        elif service_type == 'event':
            service_queryset = Event.objects.all()
        elif service_type == 'survey':
            service_queryset = Survey.objects.all()
        elif service_type == 'speciality':
            service_queryset = Speciality.objects.all()

        id_list = service_queryset.values_list('service__id', flat=True)
        return queryset.filter(id__in=id_list)

    class Meta:
        model = Record
        fields = [
            'name',
            'done',
            'date_of_creation',
            'date_start',
            'date_end',
            'editable',
            'service_type'
        ]


class RecordServiceFilter(filters.FilterSet):
    service_type = filters.ChoiceFilter(field_name='service_type', choices=SERVICE_CHOICES, method='filter_service_type')

    def filter_service_type(self, queryset, name, value):
        service_queryset = queryset.none()
        service_type = value.lower()

        if service_type == 'procedure':
            service_queryset = Procedure.objects.all()
        elif service_type == 'event':
            service_queryset = Event.objects.all()
        elif service_type == 'survey':
            service_queryset = Survey.objects.all()
        elif service_type == 'speciality':
            service_queryset = Speciality.objects.all()

        id_list = service_queryset.values_list('service__id', flat=True)
        return queryset.filter(id__in=id_list)


    class Meta:
        model = RecordService
        fields = ['service_type']

