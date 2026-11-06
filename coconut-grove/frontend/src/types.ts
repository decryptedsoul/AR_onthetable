export interface Portion {
  id: string;
  label: string;
  quantity: string;
  /** Integer minor currency units (paisa for PKR). */
  price_minor: number | null;
}

export interface Dish {
  id: string;
  name: string;
  description: string;
  category: string;
  image_url: string;
  ingredients: string[];
  example_allergens: string;
  preparation_minutes: [number, number] | null;
  spice_level: number | null;
  source_url: string | null;
  source_observed_on: string | null;
  is_sample: boolean;
  ar_status: 'planned';
  portions: Portion[];
}

export interface MenuResponse {
  restaurant: {id: string; name: string; location: string; instagram_url: string; currency: string};
  categories: {id: string; name: string}[];
  dishes: Dish[];
  total: number;
  limit: number;
  offset: number;
}
