import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export function ingestFile(sourceType, file) {
  const payload = new FormData();
  payload.append('file', file);
  payload.append('tenant', 'demo');
  return api.post(`/ingest/${sourceType}/`, payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export function fetchRecords() {
  return api.get('/records/?tenant=demo');
}

export function reviewRecord(id, payload) {
  return api.patch(`/records/${id}/review/`, payload);
}
