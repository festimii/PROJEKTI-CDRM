from django.contrib import admin
from . import models

# If Task model does not exist, comment out the line below
# admin.site.register(models.Task)

# Register other models
admin.site.register(models.ActivityLog)
admin.site.register(models.AppOpens)
# Continue registering other models as needed
