import csv
import datetime
import json
from io import StringIO

from .models import EmissionRecord

DEFAULT_FUEL_FACTORS = {
    'diesel': 2.68,
    'petrol': 2.31,
    'gasoline': 2.31,
    'lpg': 1.51,
    'fuel oil': 3.16,
}

AIRPORT_DISTANCE_OVERRIDE = {
    ('FRA', 'LHR'): 620,
    ('JFK', 'LAX'): 3983,
    ('SFO', 'ORD'): 2974,
    ('MUC', 'AMS'): 368,
}

DATE_PATTERNS = [
    '%Y-%m-%d',
    '%d.%m.%Y',
    '%d/%m/%Y',
    '%m/%d/%Y',
]

SOURCE_HEADERS = {
    'werk': 'plant',
    'lieferant': 'vendor',
    'material': 'material',
    'materialnummer': 'material_number',
    'datum': 'date',
    'menge': 'quantity',
    'einheit': 'unit',
    'kostenstelle': 'cost_center',
    'co2e': 'co2e',
    'verbrauch': 'quantity',
    'entry_date': 'date',
}

TRAVEL_FIELDS = {
    'expense_type': 'expense_type',
    'traveler': 'traveler',
    'departure_airport': 'departure_airport',
    'arrival_airport': 'arrival_airport',
    'distance_km': 'distance_km',
    'hotel_nights': 'hotel_nights',
    'ground_mode': 'ground_mode',
    'ground_distance_km': 'ground_distance_km',
}

UTILITY_HEADERS = {
    'site_code': 'site_code',
    'billing_period_start': 'period_start',
    'billing_period_end': 'period_end',
    'consumption': 'consumption',
    'consumption_kwh': 'consumption',
    'unit': 'unit',
    'tariff': 'tariff',
    'meter_id': 'meter_id',
}


def parse_date(value):
    value = (value or '').strip()
    for pattern in DATE_PATTERNS:
        try:
            return datetime.datetime.strptime(value, pattern).date()
        except ValueError:
            continue
    if not value:
        return None
    raise ValueError(f'Unrecognized date: {value}')


def normalize_number(value):
    value = (value or '').strip()
    if not value:
        return None
    value = value.replace(' ', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return None


def normalize_header(header):
    if header is None:
        return None
    header = header.strip().lower()
    return SOURCE_HEADERS.get(header, header)


def clean_text(value):
    return (value or '').strip()


def is_fuel_material(material):
    if not material:
        return False
    material = material.lower()
    return any(keyword in material for keyword in ['diesel', 'petrol', 'benzin', 'gasoline', 'lpg', 'fuel oil'])


def co2_from_fuel(quantity, unit, material_description):
    if not quantity or not unit:
        return None
    unit = unit.strip().lower()
    material_description = (material_description or '').lower()
    for keyword, factor in DEFAULT_FUEL_FACTORS.items():
        if keyword in material_description:
            return quantity * factor
    if unit in ['l', 'liter', 'litre']:
        return quantity * 2.68
    if unit in ['kg', 'kilogram']:
        return quantity * 3.0
    if unit in ['m3', 'cbm']:
        return quantity * 2.5
    return quantity * 2.5


def airport_distance(origin, destination):
    if not origin or not destination:
        return None
    origin = origin.strip().upper()
    destination = destination.strip().upper()
    if origin == destination:
        return 0
    pair = (origin, destination)
    reversed_pair = (destination, origin)
    if pair in AIRPORT_DISTANCE_OVERRIDE:
        return AIRPORT_DISTANCE_OVERRIDE[pair]
    if reversed_pair in AIRPORT_DISTANCE_OVERRIDE:
        return AIRPORT_DISTANCE_OVERRIDE[reversed_pair]
    if origin[0] == destination[0]:
        return 500
    return 1500


def parse_csv_rows(file_obj, header_mapping=None):
    text = file_obj.read().decode('utf-8-sig')
    sample = StringIO(text)
    reader = csv.DictReader(sample)
    if header_mapping:
        reader.fieldnames = [header_mapping.get(name.lower().strip(), name.lower().strip()) for name in reader.fieldnames]
    yield from reader


def normalize_sap_csv(file_obj, tenant):
    results = []
    errors = []
    text = file_obj.read().decode('utf-8-sig')
    sample = StringIO(text)
    reader = csv.DictReader(sample)
    normalized_fieldnames = [normalize_header(name) for name in reader.fieldnames]
    reader.fieldnames = normalized_fieldnames

    for row_number, row in enumerate(reader, start=1):
        try:
            material = clean_text(row.get('material') or row.get('material_number'))
            date_value = parse_date(row.get('date') or row.get('entry_date') or row.get('datum'))
            quantity = normalize_number(row.get('quantity') or row.get('menge'))
            unit = clean_text(row.get('unit') or row.get('einheit'))
            cost_center = clean_text(row.get('cost_center'))
            vendor = clean_text(row.get('vendor'))
            co2_override = normalize_number(row.get('co2e'))

            category = EmissionRecord.FUEL if is_fuel_material(material) else EmissionRecord.PROCUREMENT
            scope = EmissionRecord.SCOPE_1 if category == EmissionRecord.FUEL else EmissionRecord.SCOPE_3
            emission_kg_co2e = co2_override if co2_override is not None else co2_from_fuel(quantity, unit, material)
            if emission_kg_co2e is None:
                emission_kg_co2e = 0

            record = {
                'source_record_id': f'sap-{row_number}',
                'activity_type': material or 'SAP purchase line',
                'category': category,
                'scope': scope,
                'activity_date': date_value,
                'period_start': date_value,
                'period_end': date_value,
                'location_code': clean_text(row.get('plant') or row.get('werk')),
                'activity_quantity': quantity,
                'activity_unit': unit or 'unit',
                'emission_kg_co2e': emission_kg_co2e,
                'raw_payload': {k: v for k, v in row.items()},
            }
            results.append(record)
        except Exception as exc:
            errors.append({'row': row_number, 'reason': str(exc), 'payload': row})
    return results, errors


def normalize_utility_csv(file_obj, tenant):
    results = []
    errors = []
    text = file_obj.read().decode('utf-8-sig')
    sample = StringIO(text)
    reader = csv.DictReader(sample)
    normalized_fieldnames = [UTILITY_HEADERS.get(name.strip().lower(), name.strip().lower()) for name in reader.fieldnames]
    reader.fieldnames = normalized_fieldnames

    for row_number, row in enumerate(reader, start=1):
        try:
            period_start = parse_date(row.get('period_start'))
            period_end = parse_date(row.get('period_end'))
            consumption = normalize_number(row.get('consumption'))
            unit = clean_text(row.get('unit') or 'kwh')
            meter_id = clean_text(row.get('meter_id'))
            tariff = clean_text(row.get('tariff'))
            site_code = clean_text(row.get('site_code'))

            if consumption is None:
                raise ValueError('Consumption value is required')
            emission_kg_co2e = consumption * 0.42

            record = {
                'source_record_id': f'utility-{row_number}',
                'activity_type': 'Electricity consumption',
                'category': EmissionRecord.ELECTRICITY,
                'scope': EmissionRecord.SCOPE_2,
                'activity_date': None,
                'period_start': period_start,
                'period_end': period_end,
                'location_code': site_code or meter_id,
                'activity_quantity': consumption,
                'activity_unit': 'kWh',
                'emission_kg_co2e': emission_kg_co2e,
                'raw_payload': {k: v for k, v in row.items()},
            }
            results.append(record)
        except Exception as exc:
            errors.append({'row': row_number, 'reason': str(exc), 'payload': row})
    return results, errors


def normalize_travel_json(file_obj, tenant):
    results = []
    errors = []
    raw_text = file_obj.read().decode('utf-8-sig')
    payload = json.loads(raw_text)
    if isinstance(payload, dict) and 'trips' in payload:
        records = payload['trips']
    elif isinstance(payload, list):
        records = payload
    else:
        raise ValueError('Expected a JSON array or {"trips": []}')

    for row_number, row in enumerate(records, start=1):
        try:
            expense_type = clean_text(row.get('expense_type') or row.get('type') or row.get('category'))
            departure = clean_text(row.get('departure_airport'))
            arrival = clean_text(row.get('arrival_airport'))
            distance = normalize_number(row.get('distance_km')) or normalize_number(row.get('ground_distance_km'))
            hotel_nights = normalize_number(row.get('hotel_nights'))
            ground_mode = clean_text(row.get('ground_mode'))
            traveler = clean_text(row.get('traveler'))
            expense_date = None
            if row.get('date'):
                expense_date = parse_date(row.get('date'))

            if expense_type.lower() in ['flight', 'airfare', 'plane']:
                category = EmissionRecord.FLIGHT
                scope = EmissionRecord.SCOPE_3
                if distance is None:
                    distance = airport_distance(departure, arrival)
                emission_kg_co2e = (distance or 0) * 0.255
                activity_quantity = distance
                activity_unit = 'km'
                activity_type = 'Business flight'
            elif expense_type.lower() in ['hotel', 'lodging']:
                category = EmissionRecord.HOTEL
                scope = EmissionRecord.SCOPE_3
                if hotel_nights is None:
                    raise ValueError('hotel_nights is required for hotel expenses')
                emission_kg_co2e = hotel_nights * 15.0
                activity_quantity = hotel_nights
                activity_unit = 'nights'
                activity_type = 'Hotel stay'
            else:
                category = EmissionRecord.GROUND_TRANSPORT
                scope = EmissionRecord.SCOPE_3
                if distance is None:
                    raise ValueError('distance_km is required for ground transport')
                emission_kg_co2e = distance * 0.2
                activity_quantity = distance
                activity_unit = 'km'
                activity_type = f'Ground transport ({ground_mode or "other"})'

            record = {
                'source_record_id': f'travel-{row_number}',
                'activity_type': activity_type,
                'category': category,
                'scope': scope,
                'activity_date': expense_date,
                'period_start': expense_date,
                'period_end': expense_date,
                'location_code': f'{departure}-{arrival}' if departure and arrival else traveler,
                'activity_quantity': activity_quantity,
                'activity_unit': activity_unit,
                'emission_kg_co2e': emission_kg_co2e,
                'raw_payload': row,
            }
            results.append(record)
        except Exception as exc:
            errors.append({'row': row_number, 'reason': str(exc), 'payload': row})
    return results, errors
