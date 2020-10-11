from django.contrib import admin
from .models import Projects, ProjectUserRelation, Tickets

# Register your models here.

admin.site.register(Projects)
admin.site.register(ProjectUserRelation)
admin.site.register(Tickets)