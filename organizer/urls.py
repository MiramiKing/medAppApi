from django.urls import include, path
from organizer.views import *


urlpatterns = [
        path('notes', NoteList.as_view(), name='note-list'),
        path('notes/<int:pk>', NoteDetail.as_view(), name='note-detail'),
        path('notes/<int:note_pk>/tasks', TaskList.as_view(), name='task-list'),
        path('notes/<int:note_pk>/tasks/<int:task_pk>', TaskDetail.as_view(), name='task-detail'),
        path('records', RecordList.as_view(), name='record-list'),
        path('records/<int:pk>', RecordDetail.as_view(), name='record-detail'),
        path('service_records', RecordServiceList.as_view(), name='record-service-list'),
        path('service_records/<int:pk>', RecordServiceDetail.as_view(), name='record-service-detail'),
        path('medpersona_service_records', RecordServiceMedPersonaList.as_view(), name='record-servier-medpersona-list'),
        path('medpersona_service_records/<int:pk>', RecordServiceMedPersonaDetail.as_view(), name='record-servier-medpersona-detail'),
]
