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

    def get_service_id(self, obj):
        record_service = RecordService.objects.get(record=obj.id)
        return record_service.service.id