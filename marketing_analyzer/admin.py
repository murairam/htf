from django.contrib import admin
from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('analysis_id', 'barcode', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('analysis_id', 'barcode', 'objectives')
    readonly_fields = ('analysis_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('analysis_id', 'barcode', 'objectives', 'image')
        }),
        ('Status', {
            'fields': ('status', 'result_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
