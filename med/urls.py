from django.urls import include, path

from .views import *

urlpatterns = [
    path('registration', RegistrationAPIView.as_view()),  # post регистрация
    path('users/login', LoginAPIView.as_view()),  # post вход
    path('users', UserProfileListCreateView.as_view()),  #
    path('patients', PatientListCreateView.as_view()),
    path('medics', MedPersobaListCreateView.as_view()),
    path('medics/<int:pk>/servicemedper', ServiceMedPersonaByMedicView.as_view()),
    path('admins', AdminListCreateView.as_view()),
    path('passports', PassportDataView.as_view()),
    path('passports/<int:pk>', SinglePassportDataView.as_view()),
    path('users/<int:pk>', UserProfileDetailView.as_view()),
    path('patients/<int:pk>', PatientDetailView.as_view()),
    path('users/patients/<int:pk>/medcard', MedCardView.as_view()),
    path('medics/<int:pk>', MedPersonaDetailView.as_view()),
    path('admins/<int:pk>', AdminProfileDetailView.as_view()),
    path('user', UserRetrieveUpdateAPIView.as_view()),
    path('medpersona', MedPersonaAPIView.as_view()),
    path('patient', PatientAPIView.as_view()),
    path('passport', PassportDataByUserAPIView.as_view()),
    path('users/<int:pk>/passport', PassportDataByUserAPIView.as_view()),
    path('admin', AdminAPIView.as_view()),
    path('sanatorium', SanatoriumView.as_view()),
    path('sanatorium/<int:pk>', SingleSanatoriumView.as_view()),
    path('timetable', TimetableView.as_view()),
    path('timetable/<int:pk>', SingleTimeTableView.as_view()),
    path('service', ServiceView.as_view()),
    path('service/<int:pk>', SingleServiceView.as_view()),
    path('service/<int:service>/servicemedper', ServiceMedPersonaByServiceView.as_view()),
    path('service/<int:service>/event', SingleEventViewByService.as_view()),
    path('service/<int:service>/procedure', SingleProcedureViewByService.as_view()),
    path('service/<int:service>/survey', SingleSurveyViewByService.as_view()),
    path('service/<int:service>/speciality', ServiceMedPersonaByServiceView.as_view()),
    path('servicemedper', ServiceMedPersonaView.as_view()),
    path('servicemedper/', ServiceMedPersonaViewByIdIn.as_view()),
    path('servicemedper/<int:pk>', SingleServiceMedPersonaView.as_view()),
    path('procedure', ProcedureView.as_view()),
    path('procedure/<int:pk>', SingleProcedureView.as_view()),
    path('survey', SurveyView.as_view()),
    path('survey/<int:pk>', SingleSurveyView.as_view()),
    path('speciality', SpecialityView.as_view()),
    path('speciality/<int:pk>', SingleSpecialityView.as_view()),
    path('event', EventView.as_view()),
    path('event/<int:pk>', SingleEventView.as_view()),

]
