from django.db import models

try:
    JSONFIELD = models.JSONField
except AttributeError:
    from django.contrib.postgres.fields import JSONField as JSONFIELD

class Tenant(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SourceSystem(models.Model):
    SAP_FUEL = 'sap_fuel'
    SAP_PROCUREMENT = 'sap_procurement'
    UTILITY_ELECTRICITY = 'utility_electricity'
    CORPORATE_TRAVEL = 'corporate_travel'

    SOURCE_CHOICES = [
        (SAP_FUEL, 'SAP Fuel'),
        (SAP_PROCUREMENT, 'SAP Procurement'),
        (UTILITY_ELECTRICITY, 'Utility Electricity'),
        (CORPORATE_TRAVEL, 'Corporate Travel'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sources')
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64)
    source_type = models.CharField(max_length=32, choices=SOURCE_CHOICES)
    configuration = JSONFIELD(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('tenant', 'slug')]

    def __str__(self):
        return f'{self.name} ({self.get_source_type_display()})'

class IngestionBatch(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='batches')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE, related_name='batches')
    file_name = models.CharField(max_length=256)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.source_system.slug} @ {self.uploaded_at.isoformat()}'

class EmissionRecord(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (APPROVED, 'Approved'),
        (FAILED, 'Failed Ingestion'),
    ]

    SCOPE_1 = 'scope_1'
    SCOPE_2 = 'scope_2'
    SCOPE_3 = 'scope_3'

    SCOPE_CHOICES = [
        (SCOPE_1, 'Scope 1'),
        (SCOPE_2, 'Scope 2'),
        (SCOPE_3, 'Scope 3'),
    ]

    FUEL = 'fuel'
    PROCUREMENT = 'procurement'
    ELECTRICITY = 'electricity'
    FLIGHT = 'flight'
    HOTEL = 'hotel'
    GROUND_TRANSPORT = 'ground_transport'

    CATEGORY_CHOICES = [
        (FUEL, 'Fuel'),
        (PROCUREMENT, 'Procurement'),
        (ELECTRICITY, 'Electricity'),
        (FLIGHT, 'Flight'),
        (HOTEL, 'Hotel'),
        (GROUND_TRANSPORT, 'Ground Transport'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='emission_records')
    batch = models.ForeignKey(IngestionBatch, on_delete=models.SET_NULL, related_name='records', null=True, blank=True)
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE, related_name='records')
    source_record_id = models.CharField(max_length=128, blank=True)
    raw_payload = JSONFIELD(blank=True, null=True)

    activity_type = models.CharField(max_length=64)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    scope = models.CharField(max_length=16, choices=SCOPE_CHOICES)

    activity_date = models.DateField(null=True, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    location_code = models.CharField(max_length=128, blank=True)
    activity_quantity = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)
    activity_unit = models.CharField(max_length=32, blank=True)
    emission_kg_co2e = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    emission_unit = models.CharField(max_length=16, default='kgCO2e')

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    review_comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.CharField(max_length=128, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.category} {self.activity_type} {self.status}'
