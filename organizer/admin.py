from django.db.models import Model
from django.contrib import admin
import organizer
import inspect
import med

def get_models(members):
    def is_model(obj):
        return inspect.isclass(obj) and issubclass(obj, Model) and not obj._meta.abstract;
    return set(obj for name, obj in members if is_model(obj))

med_models = get_models(inspect.getmembers(med.models))
organizer_models = get_models(inspect.getmembers(organizer.models))

for obj in organizer_models - med_models:
    admin.site.register(obj)
