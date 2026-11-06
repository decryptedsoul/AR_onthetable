import type {MenuResponse} from './types';

const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const restaurant = encodeURIComponent(import.meta.env.VITE_RESTAURANT_ID || 'coconut-grove');

export async function getMenu(query: string, category: string, offset: number, signal: AbortSignal, savedIds?: string[]): Promise<MenuResponse> {
  const params = new URLSearchParams({q: query, limit: '24', offset: String(offset)});
  if (category) params.set('category', category);
  if (savedIds) for (const id of savedIds.length ? savedIds : ['__no_saved_dishes__']) params.append('dish_ids', id);
  const response = await fetch(`${base}/api/v1/restaurants/${restaurant}/menu?${params}`, {
    signal, headers: {Accept: 'application/json'},
  });
  if (!response.ok) throw new Error('The menu is temporarily unavailable. Please try again.');
  return response.json() as Promise<MenuResponse>;
}

