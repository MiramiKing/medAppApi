from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView,
                                     CreateAPIView, DestroyAPIView)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from medAppApi.license import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from .serializers import *
from .renderers import *
from rest_framework.renderers import JSONRenderer
from .filters import *


class UserProfileListCreateView(ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsUserAdmin]

    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    renderer_classes = (UserJSONRenderer,)
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Здесь нечего валидировать или сохранять. Мы просто хотим, чтобы
        # сериализатор обрабатывал преобразования объекта User во что-то, что
        # можно привести к json и вернуть клиенту.
        user = get_object_or_404(UserProfile, id=kwargs['pk'])
        serializer = self.serializer_class(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, id=kwargs['pk'])
        user.delete()
        return Response(status=status.HTTP_200_OK)


class PatientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class AdminProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class MedPersonaDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MedPersona.objects.all()
    serializer_class = MedPeronaSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_classes = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        serializer = self.serializer_classes(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Обратите внимание, что мы не вызываем метод save() сериализатора, как
        # делали это для регистрации. Дело в том, что в данном случае нам
        # нечего сохранять. Вместо этого, метод validate() делает все нужное.

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data.pop('email')
        # data.pop('username')

        return Response(data, status=status.HTTP_200_OK)


class MedPersobaListCreateView(ListCreateAPIView):
    queryset = MedPersona.objects.all()
    serializer_class = MedPeronaSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class PatientListCreateView(ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class AdminListCreateView(ListCreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    # renderer_classes = (JSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # Здесь нечего валидировать или сохранять. Мы просто хотим, чтобы
        # сериализатор обрабатывал преобразования объекта User во что-то, что
        # можно привести к json и вернуть клиенту.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class MedPersonaAPIView(APIView):
    serializer_class = MedPeronaSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        medpersona = get_object_or_404(MedPersona, user=request.user.id)
        serializer = self.serializer_class(medpersona)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer_data = request.data.get('medpersona', {})
        serializer_data['user'] = request.user.id
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        serializer_data = request.data.get('medpersona', {})
        medpersona = get_object_or_404(MedPersona, user=request.user.id)
        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(medpersona, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class PatientAPIView(APIView):
    serializer_class = PatientSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated, IsUserPatient]

    def get(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, user=request.user.id)
        serializer = self.serializer_class(patient)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PatientSerializer)
    def post(self, request):
        serializer_data = request.data.get('patient', {})
        serializer_data['user'] = request.user.id
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class AdminAPIView(APIView):
    serializer_class = AdminSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated, IsUserAdmin]

    def get(self, request, *args, **kwargs):
        patient = get_object_or_404(Admin, user=request.user.id)
        serializer = self.serializer_class(patient)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PatientSerializer)
    def post(self, request):
        serializer_data = request.data.get('admin', {})
        serializer_data['user'] = request.user.id
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class PassportDataAPIView(APIView):
    serializer_class = PassportDataSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        passport = get_object_or_404(PassportData, user=request.user.id)
        serializer = self.serializer_class(passport)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PatientSerializer)
    def post(self, request):
        serializer_data = request.data.get('passport', {})
        serializer_data['user'] = request.user.id
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        serializer_data = request.data.get('passport', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class PassportDataByUserAPIView(APIView):
    serializer_class = PassportDataSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        passport = get_object_or_404(PassportData, user=kwargs['pk'])
        serializer = self.serializer_class(passport)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PassportDataView(ListCreateAPIView):
    queryset = PassportData.objects.all()
    serializer_class = PassportDataSerializer
    renderer_classes = [JSONRenderer]


class SinglePassportDataView(RetrieveUpdateDestroyAPIView):
    queryset = PassportData.objects.all()
    serializer_class = PassportDataSerializer
    renderer_classes = [JSONRenderer]


class SanatoriumView(ListCreateAPIView):
    queryset = Sanatorium.objects.all()
    serializer_class = SanatoriumSerializer
    renderer_classes = [JSONRenderer]


class SingleSanatoriumView(RetrieveUpdateDestroyAPIView):
    queryset = Sanatorium.objects.all()
    serializer_class = SanatoriumSerializer
    renderer_classes = [JSONRenderer]


class TimetableView(ListCreateAPIView):
    queryset = TimeTable.objects.all()
    serializer_class = TimeTableSerializer
    renderer_classes = [JSONRenderer]
    filterset_class = TimetableFilter


class SingleTimeTableView(RetrieveUpdateDestroyAPIView):
    queryset = TimeTable.objects.all()
    serializer_class = TimeTableSerializer
    renderer_classes = [JSONRenderer]


class ServiceView(ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    renderer_classes = [JSONRenderer]


class SingleServiceView(RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    renderer_classes = [JSONRenderer]


class ServiceMedPersonaView(ListCreateAPIView):
    queryset = ServiceMedPersona.objects.all()
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = [JSONRenderer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class ServiceMedPersonaViewByIdIn(APIView):
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = [JSONRenderer]

    def get(self, request):
        medpersona = request.data.get('medpersona', {})
        if not medpersona:
            service = request.data.get('service', {})
            if not service:
                return Response({'errors': {'medpersona or service id does not exist'}},
                                status=status.HTTP_400_BAD_REQUEST)
            servicemedper = ServiceMedPersona.objects.filter(service=service)
            serializer = self.serializer_class(servicemedper, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            servicemedper = ServiceMedPersona.objects.filter(medpersona=medpersona)
            serializer = self.serializer_class(servicemedper, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        medpersona = request.data.get('medpersona', {})
        if not medpersona:
            service = request.data.get('service', {})
            if not service:
                return Response({'errors': {'medpersona or service id does not exist'}},
                                status=status.HTTP_400_BAD_REQUEST)
            servicemedper = ServiceMedPersona.objects.filter(service=service)
            serializer = self.serializer_class(servicemedper, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            servicemedper = ServiceMedPersona.objects.filter(medpersona=medpersona)
            serializer = self.serializer_class(servicemedper, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SingleServiceMedPersonaView(RetrieveUpdateDestroyAPIView):
    queryset = ServiceMedPersona.objects.all()
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = [JSONRenderer]


class ServiceMedPersonaByServiceView(ListCreateAPIView):
    queryset = ServiceMedPersona.objects.all()
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        servicemedpers = ServiceMedPersona.objects.filter(service=kwargs['pk'])
        serializer = self.serializer_class(servicemedpers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceMedPersonaByMedicView(ListCreateAPIView):
    queryset = ServiceMedPersona.objects.all()
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        servicemedpers = ServiceMedPersona.objects.filter(medpersona=kwargs['pk'])
        serializer = self.serializer_class(servicemedpers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProcedureView(ListCreateAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleProcedureView(RetrieveUpdateDestroyAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        procedure = get_object_or_404(Procedure, id=kwargs['pk'])
        serializer = self.serializer_class(procedure)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleProcedureViewByService(RetrieveUpdateDestroyAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        procedure = get_object_or_404(Procedure, service=kwargs['pk'])
        serializer = self.serializer_class(procedure)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SurveyView(ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleSurveyView(RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, id=kwargs['pk'])
        serializer = self.serializer_class(survey)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleSurveyViewByService(RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, service=kwargs['pk'])
        serializer = self.serializer_class(survey)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SpecialityView(ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    renderer_classes = [JSONRenderer]


class SingleSpecialityView(RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    renderer_classes = [JSONRenderer]


class SingleSpecialityViewByService(RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        speciality = get_object_or_404(Speciality, service=kwargs['pk'])
        serializer = self.serializer_class(speciality)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EventView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleEventView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs['pk'])
        serializer = self.serializer_class(event)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleEventViewByService(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        event = get_object_or_404(Event, service=kwargs['pk'])
        serializer = self.serializer_class(event)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MedCardView(CreateAPIView, RetrieveUpdateAPIView):
    queryset = Medcard.objects.all()
    serializer_class = MedcardSerializer
    renderer_classes = [JSONRenderer]

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'])
        medcard = get_object_or_404(Medcard, patient=patient)
        serializer = self.serializer_class(medcard)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'])
        data = request.data
        data["patient"] = patient.pk
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'])
        medcard = get_object_or_404(Medcard, patient=patient)
        serializer = self.serializer_class(medcard, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MedPersonaPatientAPIView(ListCreateAPIView, DestroyAPIView):
    queryset = MedPersonaPatient.objects.all()
    serializer_class = MedPersonaPatientSerializer
    permission_classes = [IsAuthenticated]

    renderer_classes = (JSONRenderer,)
    filter_backends = [DjangoFilterBackend]
    filter_fields = ('patient', 'medpersona', 'id')

    def get(self, request, *args, **kwargs):
        qs = self.queryset.none()
        if not request.query_params:
            qs = MedPersonaPatient.objects.all()
            serializer_data = self.serializer_class(data=qs, many=True)
            serializer_data.is_valid(raise_exception=True)
            return Response(data=serializer_data.data, status=status.HTTP_200_OK)
        elif set(request.query_params.dict().keys()).issubset(list(self.filter_fields)):
            try:
                qs_ = self.filter_queryset(self.get_queryset())
                serializer_data = self.serializer_class(qs_, many=True)

                return Response(data=serializer_data.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data=qs, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(data=qs, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, *args, **kwargs):
        if set(request.query_params.dict().keys()).issubset(list(self.filter_fields)):
            qs = self.filter_queryset(self.get_queryset())
            qs.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
