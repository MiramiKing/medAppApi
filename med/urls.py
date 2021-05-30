from django.urls import include, path

from .views import *

urlpatterns = [
    path('registration', RegistrationAPIView.as_view()),
    path('users/login', LoginAPIView.as_view()),
    path('users',UserProfileListCreateView.as_view()),
    path('user', UserRetrieveUpdateAPIView.as_view()),
    path('medpersona', MedPersonaAPIView.as_view()),
    path('patient', PatientAPIView.as_view()),
    path('passport', PassportDataAPIView.as_view()),
    path('admin', AdminAPIView.as_view()),
    path('sanatorium', SanatoriumView.as_view()),
    path('sanatorim/<int:pk>', SingleSanatoriumView.as_view()),
    path('timetable', TimetableView.as_view()),
    path('timetable/<int:pk>', SingleTimeTableView.as_view()),
    path('service', ServiceView.as_view()),
    path('service/<int:pk>', SingleServiceView.as_view()),
    path('servicemedper', ServiceMedPersonaView.as_view()),
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
