export type Product = {
  id: number;
  name: string;
  description: string;
  category: string;
  price: number;
  stock: number;
  rating: number;
  brand: string;
  features: string[];
  image: string;
};

export type ProductDetail = Product & {
  reviews: Array<{
    id: number;
    product_id: number;
    rating: number;
    comment: string;
  }>;
  related_products: Product[];
};

export type Overview = {
  revenue: number;
  orders: number;
  customers: number;
  average_rating: number;
  inventory: number;
};

export type DashboardData = {
  overview: Overview;
  sales_by_month: Array<{ month: string; revenue: number; orders: number }>;
  revenue_by_category: Array<{ category: string; revenue: number }>;
  top_products: Array<{ id: number; name: string; revenue: number; units_sold: number }>;
  stock_levels: Array<{ id: number; name: string; category: string; stock: number; rating: number; brand: string; price: number }>;
  low_stock_products: Array<{ id: number; name: string; category: string; stock: number; price: number; rating: number; brand: string }>;
  recent_orders: Array<{ id: number; product_id: number; product_name: string; quantity: number; price: number; created_at: string }>;
  bad_review_products: Array<{ id: number; name: string; avg_rating: number; review_count: number }>;
  analytics_summary: unknown;
};

export type AnalyticsData = {
  monthly_sales: Array<{ month: string; revenue: number; orders: number }>;
  category_revenue: Array<{ category: string; revenue: number }>;
  inventory_snapshot: Array<{ id: number; name: string; category: string; stock: number; rating: number; brand: string; price: number }>;
  review_summary: Array<{ id: number; product_id: number; product_name: string; category: string; rating: number; comment: string }>;
  top_products: Array<{ id: number; name: string; revenue: number; units_sold: number }>;
  summary: Overview;
};

export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export type ChatResponse = {
  answer: string;
  tool_results: Array<Record<string, unknown>>;
};
