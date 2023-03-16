from django.contrib import admin
from .models import User, Note
# Register your models here.


admin.site.register(User)
admin.site.register(Note)

class NoteAdmin(admin.ModelAdmin):
    list_display=['title', 'body']
    list_filter=['created']