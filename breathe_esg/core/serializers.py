from rest_framework import serializers

from .models import EmissionRecord, IngestionBatch, SourceSystem, Tenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug']

class SourceSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceSystem
        fields = ['id', 'name', 'slug', 'source_type', 'configuration']

class IngestionBatchSerializer(serializers.ModelSerializer):
    source_system = SourceSystemSerializer(read_only=True)

    class Meta:
        model = IngestionBatch
        fields = ['id', 'tenant', 'source_system', 'file_name', 'uploaded_at', 'row_count', 'status', 'notes']
        read_only_fields = ['uploaded_at', 'row_count', 'status']

class EmissionRecordSerializer(serializers.ModelSerializer):
    source_system = SourceSystemSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = EmissionRecord
        fields = [
            'id', 'tenant', 'batch', 'source_system', 'source_record_id', 'raw_payload',
            'activity_type', 'category', 'scope', 'activity_date', 'period_start', 'period_end',
            'location_code', 'activity_quantity', 'activity_unit', 'emission_kg_co2e', 'emission_unit',
            'status', 'review_comments', 'reviewed_at', 'reviewed_by', 'locked_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['tenant', 'source_system', 'raw_payload', 'created_at', 'updated_at', 'reviewed_at', 'locked_at']

class EmissionRecordReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionRecord
        fields = ['status', 'review_comments', 'reviewed_by']
