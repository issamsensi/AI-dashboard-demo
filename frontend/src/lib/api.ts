import type { AnalyticsData, ChatMessage, ChatResponse, DashboardData, Product, ProductDetail } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getProducts(params?: { search?: string; category?: string; limit?: number }) {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.category) query.set('category', params.category);
  if (params?.limit) query.set('limit', String(params.limit));
  return request<Product[]>(`/products${query.toString() ? `?${query.toString()}` : ''}`);
}

export function getProduct(productId: number) {
  return request<ProductDetail>(`/products/${productId}`);
}

export function getDashboard() {
  return request<DashboardData>('/dashboard');
}

export function getAnalytics() {
  return request<AnalyticsData>('/analytics');
}

export function sendCustomerChat(message: string, history: ChatMessage[]) {
  return request<ChatResponse>('/chat/customer', {
    method: 'POST',
    body: JSON.stringify({ message, history }),
  });
}

export function sendAdminChat(message: string, history: ChatMessage[]) {
  return request<ChatResponse>('/chat/admin', {
    method: 'POST',
    body: JSON.stringify({ message, history }),
  });
}
