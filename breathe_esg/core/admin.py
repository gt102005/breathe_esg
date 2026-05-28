from django.contrib import admin

from .models import EmissionRecord, IngestionBatch, SourceSystem, Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']

@admin.register(SourceSystem)
class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'source_type', 'tenant', 'created_at']
    list_filter = ['source_type']
    search_fields = ['name', 'slug']

@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'tenant', 'source_system', 'row_count', 'status', 'uploaded_at']
    list_filter = ['status', 'source_system__source_type']
    search_fields = ['file_name']

@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'category', 'scope', 'status', 'tenant', 'created_at']
    list_filter = ['category', 'scope', 'status', 'source_system__source_type']
    search_fields = ['activity_type', 'source_record_id', 'location_code']
