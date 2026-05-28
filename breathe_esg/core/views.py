import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmissionRecord, IngestionBatch, SourceSystem, Tenant
from .normalizers import normalize_sap_csv, normalize_utility_csv, normalize_travel_json
from .serializers import EmissionRecordSerializer, EmissionRecordReviewSerializer, IngestionBatchSerializer

SOURCE_CONFIG = {
    'sap': {'slug': 'sap', 'name': 'SAP exports', 'source_type': SourceSystem.SAP_FUEL},
    'utility': {'slug': 'utility', 'name': 'Utility export', 'source_type': SourceSystem.UTILITY_ELECTRICITY},
    'travel': {'slug': 'travel', 'name': 'Corporate travel', 'source_type': SourceSystem.CORPORATE_TRAVEL},
}


def get_tenant(slug):
    tenant, _ = Tenant.objects.get_or_create(slug=slug, defaults={'name': slug.title()})
    return tenant


def get_source_system(tenant, slug, name, source_type):
    source, _ = SourceSystem.objects.get_or_create(
        tenant=tenant,
        slug=slug,
        defaults={'name': name, 'source_type': source_type},
    )
    return source


def create_batch(tenant, source_system, file_name):
    return IngestionBatch.objects.create(
        tenant=tenant,
        source_system=source_system,
        file_name=file_name,
        status=IngestionBatch.PENDING,
    )


def create_records(batch, source_system, normalized_records, tenant):
    objects = []
    for normalized in normalized_records:
        obj = EmissionRecord(
            tenant=tenant,
            batch=batch,
            source_system=source_system,
            source_record_id=normalized.get('source_record_id', ''),
            raw_payload=normalized.get('raw_payload', {}),
            activity_type=normalized.get('activity_type', ''),
            category=normalized.get('category', EmissionRecord.PROCUREMENT),
            scope=normalized.get('scope', EmissionRecord.SCOPE_3),
            activity_date=normalized.get('activity_date'),
            period_start=normalized.get('period_start'),
            period_end=normalized.get('period_end'),
            location_code=normalized.get('location_code', ''),
            activity_quantity=normalized.get('activity_quantity'),
            activity_unit=normalized.get('activity_unit', ''),
            emission_kg_co2e=normalized.get('emission_kg_co2e'),
        )
        objects.append(obj)
    EmissionRecord.objects.bulk_create(objects)
    return len(objects)


class IngestAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, source_type):
        tenant_slug = request.data.get('tenant', 'demo')
        tenant = get_tenant(tenant_slug)
        if source_type not in SOURCE_CONFIG:
            return Response({'detail': 'Unknown source type.'}, status=status.HTTP_400_BAD_REQUEST)

        config = SOURCE_CONFIG[source_type]
        source_system = get_source_system(tenant, config['slug'], config['name'], config['source_type'])
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'detail': 'A file upload is required.'}, status=status.HTTP_400_BAD_REQUEST)

        batch = create_batch(tenant, source_system, file_obj.name)
        try:
            if source_type == 'sap':
                normalized, errors = normalize_sap_csv(file_obj, tenant)
            elif source_type == 'utility':
                normalized, errors = normalize_utility_csv(file_obj, tenant)
            else:
                normalized, errors = normalize_travel_json(file_obj, tenant)

            count = create_records(batch, source_system, normalized, tenant)
            batch.row_count = count
            batch.status = IngestionBatch.COMPLETED if not errors else IngestionBatch.FAILED
            batch.notes = json.dumps(errors, default=str) if errors else ''
            batch.save()
            return Response({'created': count, 'errors': errors})
        except Exception as exc:
            batch.status = IngestionBatch.FAILED
            batch.notes = str(exc)
            batch.save()
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EmissionRecordListView(generics.ListAPIView):
    serializer_class = EmissionRecordSerializer
    queryset = EmissionRecord.objects.select_related('tenant', 'source_system').order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        source_filter = self.request.query_params.get('source')
        tenant_slug = self.request.query_params.get('tenant', 'demo')
        if tenant_slug:
            qs = qs.filter(tenant__slug=tenant_slug)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if source_filter:
            qs = qs.filter(source_system__slug=source_filter)
        return qs


class EmissionRecordReviewView(APIView):
    def patch(self, request, pk):
        record = get_object_or_404(EmissionRecord, pk=pk)
        serializer = EmissionRecordReviewSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        record.reviewed_at = timezone.now()
        record.locked_at = timezone.now() if serializer.validated_data.get('status') == EmissionRecord.APPROVED else record.locked_at
        serializer.save()
        return Response(EmissionRecordSerializer(record).data)
