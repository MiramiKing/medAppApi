from django.urls import include, path
from rest_framework import routers
from organizer.views import *

baseRouter = routers.SimpleRouter()
baseRouter.register(r'records', RecordViewSet, basename='record')

recordRouter = routers.SimpleRouter()
# recordRouter.register(r'service', ServiceRecordViewSet, basename='service')
# recordRouter.register(r'medicine', MedicineRecordViewSet, basename='medicine')

urlpatterns = [
        # path(r'records/', include(recordRouter.urls)),
        path('', include(baseRouter.urls)),
]
