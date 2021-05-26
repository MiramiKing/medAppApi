# from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.status import *
from organizer.serializers import *
from organizer.models import *
from med.models import ServiceMedPersona
# from organizer import _queryset_

# Для RecordServiceMedPersona
def check_service_medpersona(service_id, medpersona_id):
    if service_id is None:
        return Response(data={'errors':{'service_id': 'this field is required'}}, status=HTTP_400_BAD_REQUEST)
    if medpersona_id is None:
        return Response(data={'errors':{'medpersona_id': 'this field is required'}}, status=HTTP_400_BAD_REQUEST)

    # удостовериться, что такая услуга существует
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        service = None

    # удостовериться, что такая медперсона существует
    try:
        medpersona = MedPersona.objects.get(id=medpersona_id)
    except MedPersona.DoesNotExist:
        medpersona = None
    return service, medpersona


class RecordList(ListCreateAPIView):
    queryset = Record.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]

    # def list(self, request, *args, **kwargs):
    #     qs, err = _queryset_.filter(request.query_params, self.queryset)
    #     if err is not None:
    #         return Response(data={'errors': {'details': err}}, status=HTTP_400_BAD_REQUEST)

    #     serializer = self.serializer_class(qs.all(), many=True)
    #     return Response(serializer.data, status=HTTP_200_OK)


class RecordDetail(RetrieveUpdateDestroyAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    renderer_classes = [JSONRenderer]


class RecordServiceList(ListCreateAPIView):
    model = Record
    serializer_class = RecordServiceSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        id_list = RecordService.objects.values_list('record__id', flat=True)
        return Record.objects.filter(id__in=id_list)

    # def list(self, request, *args, **kwargs):
    #     qs, err = _queryset_.filter(request.query_params, self.get_queryset())
    #     if err is not None:
    #         return Response(data={'errors': {'details': err}}, status=HTTP_400_BAD_REQUEST)
        
    #     serializer = self.serializer_class(qs.all(), many=True)
    #     return Response(serializer.data, status=HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        service_id = data.pop('service_id', None)
        if service_id is None:
            return Response(data={'errors':{'service_id': 'this field is required'}}, status=HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'errors': {'service_id': 'service {} does not exist'.format(service_id)}}, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data)
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
            return Response(data={'errors':{'service_id': 'this field is required'}}, status=HTTP_400_BAD_REQUEST)

        # если в БД нет услуги с таким id, то отклоняем
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'errors': {'service_id': 'service {} does not exist'.format(service_id)}}, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(record, data=data)
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



class RecordServiceMedPersonaList(ListCreateAPIView):
    model = Record
    serializer_class = RecordMedPersonaSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        id_list = RecordServiceMedPersona.objects.values_list('record_service__record__id', flat=True)
        return Record.objects.filter(id__in=id_list)

    # def list(self, request, *args, **kwargs):
    #     qs, err = _queryset_.filter(request.query_params, self.get_queryset())
    #     if err is not None:
    #         return Response(data={'errors': {'details': err}}, status=HTTP_400_BAD_REQUEST)

    #     serializer = self.serializer_class(qs.all(), many=True)
    #     return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        service_id = data.pop('service_id', None)
        medpersona_id = data.pop('medpersona_id', None)

        service, medpersona = check_service_medpersona(service_id, medpersona_id)
        if service is None:
            return Response({'errors': {'service_id': 'service {} does not exist'.format(service_id)}}, status=HTTP_400_BAD_REQUEST)
        if medpersona is None:
            return Response({'errors': {'medpersona_id': 'medpersona {} does not exist'.format(medpersona_id)}}, status=HTTP_400_BAD_REQUEST)

        # нужно удостовериться, что медперсона действительно имеет конкретную услугу
        try:
            service_medpersona = ServiceMedPersona.objects.get(service=service, medpersona=medpersona)
        except ServiceMedPersona.DoesNotExist:
            return Response({'errors': {'medpersona_id': 'medpersona {} does not have service {}'.format(medpersona_id, service_id)}}, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            # создаем запись
            new_record = serializer.save()
            # запись услуги
            record_service = RecordService.objects.create(service=service, record=new_record)
            # запись услуги-медперсонала
            RecordServiceMedPersona.objects.create(record_service=record_service, medpersona=medpersona)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class RecordServiceMedPersonaDetail(RetrieveUpdateDestroyAPIView):
    model = Record
    serializer_class = RecordMedPersonaSerializer
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        id_list = RecordServiceMedPersona.objects.values_list('record_service__record__id', flat=True)
        return Record.objects.filter(id__in=id_list)

    def update(self, request, *args, **kwargs):
        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response({'errors': 'record {} does not exist'.format(kwargs['pk'])}, status=HTTP_400_BAD_REQUEST)

        data = JSONParser().parse(request)
        service_id = data.pop('service_id', None)
        medpersona_id = data.pop('medpersona_id', None)

        service, medpersona = check_service_medpersona(service_id, medpersona_id)
        if service is None:
            return Response({'errors': {'service_id': 'service {} does not exist'.format(service_id)}}, status=HTTP_400_BAD_REQUEST)
        if medpersona is None:
            return Response({'errors': {'medpersona_id': 'medpersona {} does not exist'.format(medpersona_id)}}, status=HTTP_400_BAD_REQUEST)

        # нужно удостовериться, что медперсона действительно имеет конкретную услугу
        try:
            service_medpersona = ServiceMedPersona.objects.get(service=service, medpersona=medpersona)
        except ServiceMedPersona.DoesNotExist:
            return Response({'errors': {'medpersona_id': 'medpersona {} does not have service {}'.format(medpersona_id, service_id)}}, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(record, data=data)
        if serializer.is_valid():
            # обновляем данные записи
            updated_record = serializer.save()
            # находим запись-услугу
            record_service = RecordService.objects.get(record=updated_record)
            # перезаписываем услугу
            record_service.service = service
            # сохраняем
            record_service.save()
            # находим запись-услуга-медперсону
            record_service_medpersona = RecordServiceMedPersona.objects.get(record_service=record_service)
            # перезаписываем медперсону
            record_service_medpersona.medpersona = medpersona
            # и сохраняем
            record_service_medpersona.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST) 


    def destroy(self, request, *args, **kwargs):
        try:
            record = Record.objects.get(pk=kwargs['pk'])
        except Record.DoesNotExist:
            return Response({'errors': 'record {} does not exist'.format(kwargs['pk'])}, status=HTTP_404_NOT_FOUND)

        record.delete()
        return Response(status=HTTP_204_NO_CONTENT)
