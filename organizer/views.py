# from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.status import *
from organizer.serializers import *
from organizer.models import *


class RecordList(ListCreateAPIView):
    queryset = Record.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]


class RecordDetail(RetrieveUpdateDestroyAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]


class RecordServiceList(ListCreateAPIView):
    model = Record
    serializer_class = RecordServiceSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        id_list = RecordService.objects.values_list('record_id', flat=True)
        return Record.objects.filter(id__in=id_list)

    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        service_id = data.pop('service_id', None)
        if service_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)
        service = Service.objects.get(id=service_id)
        serializer = RecordServiceSerializer(data=data)
        if serializer.is_valid():
            new_record = serializer.save()
            RecordService.objects.create(service=service, record=new_record)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class RecordServiceDetail(RetrieveUpdateDestroyAPIView):
    model = Record
    serializer_class = RecordServiceSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        id_list = RecordService.objects.values_list('record_id', flat=True)
        return Record.objects.filter(id__in=id_list)

    def update(self, request, *args, **kwargs):
        # достаем запись из БД
        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response({'errors': 'record {} does not exist'.format(kwargs['pk'])}, status=HTTP_400_BAD_REQUEST)

        # достаем из запроса id услуги
        data = JSONParser().parse(request)
        service_id = data.pop('service_id', None)
        # если такого поля в запросе нет, то отклоняем
        if service_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        # если в БД нет услуги с таким id, то отклоняем
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'errors': {'service_id': 'service {} does not exist'.format(service_id)}}, status=HTTP_400_BAD_REQUEST)

        serializer = RecordServiceSerializer(record, data=data)
        if serializer.is_valid():
            # обновляем данные записи
            updated_record = serializer.save()
            # находим запись-услугу
            record_service = RecordService.objects.get(record=updated_record)
            # перезаписываем id услуги
            record_service.service = service
            # и сохраняем
            record_service.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST) 

    def destroy(self, request, *args, **kwargs):
        # достаем запись из БД
        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response({'errors': 'record {} does not exist'.format(kwargs['pk'])}, status=HTTP_404_NOT_FOUND)

        record.delete()
        return Response(status=HTTP_204_NO_CONTENT)

