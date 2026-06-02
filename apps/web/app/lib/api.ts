export type Brand = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  voice: string | null;
  compliance_notes: string | null;
};

export type Product = {
  id: string;
  brand_id: string;
  name: string;
  slug: string;
  category: string;
  description: string | null;
  key_benefits: string[];
  price_cents: number | null;
  active: boolean;
};

export type Campaign = {
  id: string;
  brand_id: string;
  name: string;
  objective: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  target_audience: string | null;
};

export type ContentItem = {
  id: string;
  campaign_id: string;
  product_id: string | null;
  title: string;
  channel: string;
  format: string;
  status: string;
  body: string | null;
  metadata: Record<string, unknown>;
};

export type Approval = {
  id: string;
  content_item_id: string;
  reviewer_name: string;
  status: string;
  feedback: string | null;
  decided_at: string | null;
};

const apiBaseUrl = process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchResource<T>(path: string): Promise<T[]> {
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return [];
    }

    return (await response.json()) as T[];
  } catch {
    return [];
  }
}

export function getBrands() {
  return fetchResource<Brand>("/api/brands");
}

export function getProducts() {
  return fetchResource<Product>("/api/products");
}

export function getCampaigns() {
  return fetchResource<Campaign>("/api/campaigns");
}

export function getContentItems() {
  return fetchResource<ContentItem>("/api/content-items");
}

export function getApprovals() {
  return fetchResource<Approval>("/api/approvals");
}
