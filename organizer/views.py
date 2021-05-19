from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from medAppApi.license import IsUserPatient
from organizer.serializers import RecordSerializer
from organizer.models import Record


class RecordViewSet(ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [IsUserPatient, IsAuthenticated]
