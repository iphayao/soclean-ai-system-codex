export type Brand = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  voice: string | null;
  compliance_notes: string | null;
  created_at?: string;
  updated_at?: string;
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
  created_at?: string;
  updated_at?: string;
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
  created_at?: string;
  updated_at?: string;
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
  created_at?: string;
  updated_at?: string;
};

export type Approval = {
  id: string;
  content_item_id: string;
  reviewer_name: string;
  status: string;
  feedback: string | null;
  decided_at: string | null;
  created_at?: string;
  updated_at?: string;
};

export type AgentRunStep = {
  id: string;
  step_order: number;
  step_name: string;
  status: string;
  output_metadata: Record<string, unknown>;
  error: string | null;
  started_at: string;
  completed_at: string | null;
};

export type AgentRun = {
  id: string;
  campaign_id: string;
  workflow_name: string;
  status: string;
  retry_count: number;
  run_metadata: Record<string, unknown>;
  output_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  steps: AgentRunStep[];
};

export type PerformanceMetric = {
  id: string;
  campaign_id: string | null;
  platform: string;
  metric_name: string;
  metric_value: number;
  period_start: string | null;
  period_end: string | null;
};

export type CampaignAnalytics = {
  campaign_id: string;
  platform: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  clicks: number;
  add_to_cart: number;
  orders: number;
  revenue: number;
  spend: number;
  roas: number | null;
};

export type GenerateContentResponse = {
  agent_run_id: string;
  campaign_id: string;
  status: string;
  retry_count: number;
  review_passed: boolean;
  content_item_ids: string[];
  content_items: ContentItem[];
};

export type GenerationJob = {
  id: string;
  campaign_id: string;
  celery_task_id: string | null;
  status: "queued" | "running" | "completed" | "failed";
  error: string | null;
  result_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type GenerateContentJobResponse = {
  job_id: string;
  campaign_id: string;
  status: GenerationJob["status"];
};

export type ContentExportResponse = {
  content_id: string;
  status: string;
  exported: boolean;
};

export type AnalyticsImportResponse = {
  imported: number;
};

export const API_BASE_URL =
  process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    cache: options.cache ?? "no-store",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function safeList<T>(path: string): Promise<T[]> {
  try {
    return await apiRequest<T[]>(path);
  } catch {
    return [];
  }
}

async function safeGet<T>(path: string): Promise<T | null> {
  try {
    return await apiRequest<T>(path);
  } catch {
    return null;
  }
}

async function uploadFile<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status} ${path}`);
  }

  return (await response.json()) as T;
}

export const api = {
  getBrands: () => safeList<Brand>("/api/brands"),
  getBrand: (id: string) => safeGet<Brand>(`/api/brands/${id}`),
  createBrand: (body: Partial<Brand>) => apiRequest<Brand>("/api/brands", { method: "POST", body }),
  updateBrand: (id: string, body: Partial<Brand>) => apiRequest<Brand>(`/api/brands/${id}`, { method: "PATCH", body }),

  getProducts: () => safeList<Product>("/api/products"),
  getProduct: (id: string) => safeGet<Product>(`/api/products/${id}`),
  createProduct: (body: Partial<Product>) => apiRequest<Product>("/api/products", { method: "POST", body }),
  updateProduct: (id: string, body: Partial<Product>) =>
    apiRequest<Product>(`/api/products/${id}`, { method: "PATCH", body }),

  getCampaigns: () => safeList<Campaign>("/api/campaigns"),
  getCampaign: (id: string) => safeGet<Campaign>(`/api/campaigns/${id}`),
  createCampaign: (body: Partial<Campaign>) => apiRequest<Campaign>("/api/campaigns", { method: "POST", body }),
  updateCampaign: (id: string, body: Partial<Campaign>) =>
    apiRequest<Campaign>(`/api/campaigns/${id}`, { method: "PATCH", body }),
  generateCampaignContent: (id: string) =>
    apiRequest<GenerateContentJobResponse>(`/api/campaigns/${id}/generate-content`, { method: "POST", body: {} }),
  getJob: (id: string) => apiRequest<GenerationJob>(`/api/jobs/${id}`),

  getContentItems: () => safeList<ContentItem>("/api/content-items"),
  getContentItem: (id: string) => safeGet<ContentItem>(`/api/content-items/${id}`),
  updateContentItem: (id: string, body: Partial<ContentItem>) =>
    apiRequest<ContentItem>(`/api/content-items/${id}`, { method: "PATCH", body }),
  exportContent: (id: string) =>
    apiRequest<ContentExportResponse>(`/api/content/${id}/export`, { method: "POST", body: {} }),

  getApprovals: () => safeList<Approval>("/api/approvals"),
  createApproval: (body: Partial<Approval>) => apiRequest<Approval>("/api/approvals", { method: "POST", body }),

  getAgentRuns: () => safeList<AgentRun>("/api/agent-runs"),
  importAnalyticsCsv: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return uploadFile<AnalyticsImportResponse>("/api/analytics/import-csv", formData);
  },
  getCampaignAnalytics: (campaignId: string) =>
    safeList<CampaignAnalytics>(`/api/analytics/campaigns/${campaignId}`),
};

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return "TBD";
  }
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function campaignName(campaigns: Campaign[], campaignId: string) {
  return campaigns.find((campaign) => campaign.id === campaignId)?.name ?? "Unknown campaign";
}

export function productName(products: Product[], productId: string | null) {
  if (!productId) {
    return "No product";
  }
  return products.find((product) => product.id === productId)?.name ?? "Unknown product";
}

export const getBrands = api.getBrands;
export const getProducts = api.getProducts;
export const getCampaigns = api.getCampaigns;
export const getContentItems = api.getContentItems;
export const getApprovals = api.getApprovals;
