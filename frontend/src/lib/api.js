const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function fetchEvents(limit = 100) {
  const response = await fetch(`${API_BASE_URL}/events?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch events');
  }
  return response.json();
}

export async function fetchAnomalies(limit = 100) {
  const response = await fetch(`${API_BASE_URL}/anomalies?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch anomalies');
  }
  return response.json();
}

export async function fetchMetrics() {
  const response = await fetch(`${API_BASE_URL}/metrics`);
  if (!response.ok) {
    throw new Error('Failed to fetch metrics');
  }
  return response.json();
}
