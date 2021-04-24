from django.contrib import admin

from .models import *

admin.site.register(Sanatorium)
admin.site.register(UserProfile)
admin.site.register(Admin)
admin.site.register(PasportData)
admin.site.register(Patient)
admin.site.register(Question)
admin.site.register(Form)
admin.site.register(Article)

# Register your models here.
