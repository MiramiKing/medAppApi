from rest_framework import serializers
from organizer.models import *


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


class RecordServiceSerializer(serializers.ModelSerializer):
    service_id = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = '__all__';

    def get_service_id(self, instance):
        record_service = RecordService.objects.get(record=instance.id)
        return record_service.service.id


class RecordMedPersonaSerializer(serializers.ModelSerializer):
    medpersona_id = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = '__all__'

    def get_service_id(self, instance):
        record_service = RecordService.objects.get(record=instance.id)
        return record_service.service.id

    def get_medpersona_id(self, instance):
        record_service = RecordService.objects.get(record=instance.id)
        record_service_medpersona = RecordServiceMedPersona.objects.get(record_service=record_service)
        return record_service_medpersona.medpersona.id