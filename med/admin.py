from django.contrib import admin
from django.db.models import Model
import inspect
from . import models

for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj)  and issubclass(obj, Model) and not obj._meta.abstract:
            admin.site.register(obj)


# Register your models here.
