from django.urls import include, path
from organizer.views import *


urlpatterns = [
        path('records/', RecordList.as_view()),
        path('records/<int:pk>/', RecordDetail.as_view()),
        path('records/services/', RecordServiceList.as_view()),
        path('records/services/<int:pk>/', RecordServiceDetail.as_view()),
]
