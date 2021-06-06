from rest_framework import serializers
from organizer.models import *


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


class RecordServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordService
        fields = '__all__';


class RecordMedPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordServiceMedPersona
        fields = '__all__'
