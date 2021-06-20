from rest_framework import serializers
from organizer.models import *
from med.models import Notes, Task

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


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
