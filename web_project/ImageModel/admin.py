from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'status', 'upload_time', 'creator')
    list_filter = ('status', 'model_name')
    search_fields = ('model_name', 'status')
    readonly_fields = ('upload_time',)
    date_hierarchy = 'upload_time'
