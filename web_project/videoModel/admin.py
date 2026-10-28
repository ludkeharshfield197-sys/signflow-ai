from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'status', 'detection_time', 'creator')
    list_filter = ('status',)
    search_fields = ('original_filename',)
    readonly_fields = ('detection_time', 'created_at', 'updated_at')
    date_hierarchy = 'detection_time'
