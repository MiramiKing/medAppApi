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

def get_user_notes(request, note_id):
    notes = Notes.objects.filter(user=request.user)
    if note_id == '':
        return None
    return notes.filter(id=note_id)

def get_user_tasks(request, task_id):
    tasks = Task.objects.filter(note__user=request.user)
    if task_id == '':
        return None
    return tasks.filter(id=task_id)


class NoteList(ListCreateAPIView):
    queryset = Notes.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = NoteSerializer
    renderer_classes = [JSONRenderer]

    def list(self, request, *args, **kwargs):
        notes = Notes.objects.filter(user=request.user)
        serializer = self.serializer_class(notes, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


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

    def retrieve(self, request, *args, **kwargs):
        notes = get_user_object(request, Notes.objects.all(), kwargs.get('pk', ''))
        if notes == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(notes) == 0:
            return Response(status=HTTP_404_NOT_FOUND)

        note = notes[0]

        serializer = self.serializer_class(note)
        return Response(serializer.data, status=HTTP_200_OK)


class TaskList(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = TaskSerializer
    renderer_classes = [JSONRenderer]

    def list(self, request, *args, **kwargs):
        notes = get_user_notes(request, kwargs.get('note_pk', ''))
        if notes == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(notes) == 0:
            return Response(status=HTTP_404_NOT_FOUND)

        note = notes[0]
        task = Task.objects.filter(note=note)
        serializer = self.serializer_class(task, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        notes = get_user_notes(request, kwargs.get('note_pk', ''))
        if notes == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(notes) == 0:
            return Response(status=HTTP_404_NOT_FOUND)

        request.data['note'] = notes[0].id
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
        tasks = get_user_tasks(request, kwargs.get('task_pk', ''))
        if tasks == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(tasks) == 0:
            return Response(status=HTTP_404_NOT_FOUND)
        task = tasks[0]

        serializer = self.serializer_class(task)
        return Response(serializer.data, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response(serializer.data, status=HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        # можно доставать сразу по id, потому что таблица Задач глобальная
        tasks = get_user_tasks(request, kwargs.get('task_pk', ''))

        if tasks == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(tasks) == 0:
            return Response(status=HTTP_404_NOT_FOUND)
        task = tasks[0]

        data = JSONParser().parse(request)
        serializer = self.serializer_class(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        tasks = get_user_tasks(request, kwargs.get('task_pk', ''))

        if tasks == None:
            return Response(status=HTTP_400_BAD_REQUEST)
        elif len(tasks) == 0:
            return Response(status=HTTP_404_NOT_FOUND)
        task = tasks[0]

        task.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecordList(ListCreateAPIView):
    queryset = Record.objects.all()
    permission_classes = [IsAuthenticated, IsUserPatient|IsUserMedic]
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]
    filterset_class = RecordFilter

    def get_queryset(self):
        if self.request.user.role == 'Patient':
            return Record.objects.filter(patient__user=self.request.user)
        else:
            return Record.objects.all()

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

    def retrieve(self, request, *args, **kwargs):
        if request.user.role == 'Patient':
            records = Record.objects.filter(patient__user=request.user)
        else:
            records = Record.objects.all()
        
        try:
            record = records.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(record)
        return Response(serializer.data, status=HTTP_200_OK)

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

    def get_queryset(self):
        if self.request.user.role == 'Patient':
            return RecordService.objects.filter(record__patient__user=self.request.user)
        else:
            return RecordService.objects.all()

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

    def get_queryset(self):
        if self.request.user.role == 'Patient':
            return RecordServiceMedPersona.objects.filter(record_service__record__patient__user=self.request.user)
        else:
            return RecordServiceMedPersona.objects.all()

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


