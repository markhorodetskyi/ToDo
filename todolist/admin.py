from django.contrib import admin
from .models import *


class Todo_model(admin.ModelAdmin):
    list_display = ('title', 'ended_at', 'complete')
    search_fields = ['title']


admin.site.register(Todo, Todo_model)
