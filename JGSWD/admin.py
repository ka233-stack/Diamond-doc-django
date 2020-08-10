from django.contrib import admin
from . import models

admin.site.register(models.Users)
admin.site.register(models.Doc)
admin.site.register(models.Groups)
admin.site.register(models.Comment)