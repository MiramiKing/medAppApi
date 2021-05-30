from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView,
                                     CreateAPIView)
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


class UserProfileListCreateView(ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]


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
    permission_classes = [IsAuthenticated]



class PatientListCreateView(ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]



class AdminListCreateView(ListCreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated]



class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
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


class SingleServiceMedPersonaView(RetrieveUpdateDestroyAPIView):
    queryset = ServiceMedPersona.objects.all()
    serializer_class = ServiceMedPersonaSerializer
    renderer_classes = [JSONRenderer]

class ProcedureView(ListCreateAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    renderer_classes = [JSONRenderer]


class SingleProcedureView(RetrieveUpdateDestroyAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    renderer_classes = [JSONRenderer]

class SurveyView(ListCreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    renderer_classes = [JSONRenderer]


class SingleSurveyView(RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    renderer_classes = [JSONRenderer]

class SpecialityView(ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    renderer_classes = [JSONRenderer]


class SingleSpecialityView(RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    renderer_classes = [JSONRenderer]

class EventView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    renderer_classes = [JSONRenderer]


class SingleEventView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    renderer_classes = [JSONRenderer]
