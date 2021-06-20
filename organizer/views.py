from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.status import *
from medAppApi.license import *
from med.models import Patient, Notes, Task
from organizer.serializers import *
from organizer.models import *
from organizer.filters import *


class NoteList(ListCreateAPIView):
    queryset = Notes.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = NoteSerializer
    renderer_classes = [JSONRenderer]

    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_201_CREATED)


class NoteDetail(RetrieveUpdateDestroyAPIView):
    queryset = Notes.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = NoteSerializer
    renderer_classes = [JSONRenderer]

    # def partial_update(sefl, request, *args, **kwargs):
    #     pass

    # def destroy(self, request, *args, **kwargs):
    #     pass


class TaskList(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = TaskSerializer
    renderer_classes = [JSONRenderer]

    def list(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(Task.objects.filter(note=note), many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        request.data['note'] = note.id
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)


class TaskDetail(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = TaskSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        task_queryset = Task.objects.filter(note=note)
        try:
            task = task_queryset.get(id=kwargs['task_pk'])
        except Task.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(task)
        return Response(serializer.data, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        task_queryset = Task.objects.filter(note=note)
        try:
            task = task_queryset.get(id=kwargs['task_pk'])
        except Task.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)
        serializer = self.serializer_class(task, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        task_queryset = Task.objects.filter(note=note)
        try:
            task = task_queryset.get(id=kwargs['task_pk'])
        except Task.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)
        serializer = self.serializer_class(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        try:
            note = Notes.objects.get(id=kwargs['note_pk'])
        except Notes.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        task_queryset = Task.objects.filter(note=note)
        try:
            task = task_queryset.get(id=kwargs['task_pk'])
        except Task.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecordList(ListCreateAPIView):
    queryset = Record.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]
    filterset_class = RecordFilter

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Patient':
            return Response(status=HTTP_403_FORBIDDEN)

        data = JSONParser().parse(request)

        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        data['patient'] = patient.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_201_CREATED)


class RecordDetail(RetrieveUpdateDestroyAPIView):
    queryset = Record.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'Doctor':
            return Response(status=HTTP_403_FORBIDDEN)

        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        data = JSONParser().parse(request)
        serializer = self.serializer_class(record, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'Doctor':
            return Response(status=HTTP_403_FORBIDDEN)

        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        record.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecordServiceList(ListCreateAPIView):
    queryset = RecordService.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordServiceSerializer
    renderer_classes = [JSONRenderer]
    filterset_class = RecordServiceFilter

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Patient':
            return Response(status=HTTP_403_FORBIDDEN)

        data = JSONParser().parse(request)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_201_CREATED)


class RecordServiceDetail(RetrieveAPIView):
    queryset = RecordService.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordServiceSerializer
    renderer_classes = [JSONRenderer]


class RecordServiceMedPersonaList(ListCreateAPIView):
    queryset = RecordServiceMedPersona.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordMedPersonaSerializer
    renderer_classes = [JSONRenderer]

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Patient':
            return Response(status=HTTP_403_FORBIDDEN)

        data = JSONParser().parse(request)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_201_CREATED)


class RecordServiceMedPersonaDetail(RetrieveAPIView):
    queryset = RecordServiceMedPersona.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordMedPersonaSerializer
    renderer_classes = [JSONRenderer]

    # def update(self, request, *args, **kwargs):
    #     if request.user.role is not 'Doctor':
    #         return Response(status=HTTP_403_FORBIDDEN)

    #     try:
    #         record_service_medpersona = RecordServiceMedPersona.objects.get(pk=kwargs['pk'])
    #     except RecordServiceMedPersona.DoesNotExist:
    #         return Response(status=HTTP_404_NOT_FOUND)

    #     data = JSONParser().parse(request)
    #     serializer = self.serializer_class(record_service_medpersona, data=data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     return Response(serializer.data, status=HTTP_200_OK)


