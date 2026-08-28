export type ApiImage = { url: string | null; alt_text: string; order: number; is_cover: boolean; width: number | null; height: number | null };
export type ApiProperty = {
  id: string; title: string; description: string; purpose: 'sale' | 'rent'; purpose_label: string;
  property_type: string; property_type_label: string; price: string | null; price_display: string;
  condominium_fee: string | null; total_area: string; bedrooms: number | null; suites: number | null;
  bathrooms: number | null; parking_spaces: number | null; is_featured: boolean; images: ApiImage[];
  address: { neighborhood: string; city: string; state: string; display: string };
  map: { visible: boolean; latitude?: string; longitude?: string };
};
export type PropertyPage = { count: number; next: string | null; previous: string | null; results: ApiProperty[] };
export type FilterOptions = {
  purposes: { value: string; label: string }[];
  property_types: { value: string; label: string }[];
  cities: string[];
  neighborhoods: string[];
};
export const emptyFilters: FilterOptions = { purposes: [], property_types: [], cities: [], neighborhoods: [] };

function apiBaseUrl() {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/$/, '');
  if (configured) return configured;
  if (typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)) return 'http://127.0.0.1:8000';
  throw new Error('O endereço público da API ainda não foi configurado.');
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, { signal, headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`A API respondeu com o código ${response.status}.`);
  return response.json() as Promise<T>;
}

export function fetchProperties(params: URLSearchParams, signal?: AbortSignal) {
  const query = params.toString();
  return request<PropertyPage>(`/api/v1/properties/${query ? `?${query}` : ''}`, signal);
}
export function fetchFilterOptions(signal?: AbortSignal) {
  return request<FilterOptions>('/api/v1/properties/filters/', signal);
}
export function fetchProperty(id: string, signal?: AbortSignal) {
  return request<ApiProperty>(`/api/v1/properties/${encodeURIComponent(id)}/`, signal);
}

export type InterestPayload = {
  name: string;
  phone: string;
  email: string;
  message: string;
  consent: boolean;
  website: string;
};

export async function submitInterest(id: string, payload: InterestPayload) {
  const response = await fetch(`${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(id)}/interest/`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({})) as Record<string, string | string[]>;
  if (!response.ok) {
    const message = Object.values(data).flat().join(' ');
    throw new Error(message || 'Não foi possível enviar seu interesse.');
  }
}
