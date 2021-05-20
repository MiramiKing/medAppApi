from django.urls import include, path

from .views import *

urlpatterns = [
    path('registration', RegistrationAPIView.as_view()),
    path('users/login', LoginAPIView.as_view()),
    path('user', UserRetrieveUpdateAPIView.as_view()),
    path('medpersona', MedPersonaAPIView.as_view()),
    path('patient', PatientAPIView.as_view()),
    path('passport', PassportDataAPIView.as_view()),
    path('admin',AdminAPIView.as_view())

]
