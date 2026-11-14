import { useEffect, useState } from 'react';
import { ShoppingBag, Star, TrendingUp, Users, Warehouse } from 'lucide-react';
import { ChatPanel } from '../components/ChatPanel';
import { DashboardCharts } from '../components/DashboardCharts';
import { StatCard } from '../components/StatCard';
import { getDashboard } from '../lib/api';
import type { DashboardData } from '../lib/types';

function currency(value: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    getDashboard().then(setData);
  }, []);

  if (!data) {
    return <div className="glass h-[700px] animate-pulse rounded-[2rem]" />;
  }

  return (
    <div className="space-y-8 pb-10">
      <div>
        <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Intelligent dashboard</div>
        <h1 className="mt-2 text-4xl font-display font-bold">Operational view for the AI commerce demo</h1>
        <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted)]">
          This dashboard is powered by SQLite analytics, not mock data. It shows how the admin assistant can answer operational questions using the same tables as the UI.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Revenue" value={currency(Number(data.overview.revenue))} hint="All orders in the demo database" />
        <StatCard label="Orders" value={String(data.overview.orders)} hint="Rows in the Orders table" />
        <StatCard label="Customers" value={String(data.overview.customers)} hint="Seeded customer records" />
        <StatCard label="Average Rating" value={Number(data.overview.average_rating).toFixed(2)} hint="Across catalog products" />
        <StatCard label="Inventory" value={String(data.overview.inventory)} hint="Total units on hand" />
      </section>

      <DashboardCharts
        salesByMonth={data.sales_by_month}
        revenueByCategory={data.revenue_by_category}
        topProducts={data.top_products}
        stockLevels={data.stock_levels}
      />

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Top products</div>
            <h2 className="mt-2 text-2xl font-display font-bold">Best revenue contributors</h2>
          </div>
          <div className="space-y-3">
            {data.top_products.map((product, index) => (
              <div key={product.id} className="flex items-center justify-between rounded-2xl bg-slate-900/5 px-4 py-3 dark:bg-white/5">
                <div>
                  <div className="font-semibold">#{index + 1} {product.name}</div>
                  <div className="text-sm text-[var(--muted)]">{product.units_sold} units sold</div>
                </div>
                <div className="text-right font-display text-xl font-bold">{currency(product.revenue)}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Low stock</div>
            <h2 className="mt-2 text-2xl font-display font-bold">What should be restocked</h2>
          </div>
          <div className="space-y-3">
            {data.low_stock_products.slice(0, 6).map((product) => (
              <div key={product.id} className="rounded-2xl border border-[var(--border)] bg-white/70 p-4 dark:bg-white/5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-semibold">{product.name}</div>
                    <div className="text-sm text-[var(--muted)]">{product.category} · {product.brand}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-display text-xl font-bold">{product.stock}</div>
                    <div className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">units left</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Recent orders</div>
            <h2 className="mt-2 text-2xl font-display font-bold">Latest activity</h2>
          </div>
          <div className="space-y-3">
            {data.recent_orders.map((order) => (
              <div key={order.id} className="flex items-center justify-between rounded-2xl bg-slate-900/5 px-4 py-3 dark:bg-white/5">
                <div>
                  <div className="font-semibold">{order.product_name}</div>
                  <div className="text-sm text-[var(--muted)]">{order.quantity} units · {new Date(order.created_at).toLocaleDateString()}</div>
                </div>
                <div className="text-right font-display text-lg font-bold">{currency(order.price)}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Review risk</div>
            <h2 className="mt-2 text-2xl font-display font-bold">Products with weak reviews</h2>
          </div>
          <div className="space-y-3">
            {data.bad_review_products.map((product) => (
              <div key={product.id} className="rounded-2xl border border-[var(--border)] bg-white/70 p-4 dark:bg-white/5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-semibold">{product.name}</div>
                    <div className="text-sm text-[var(--muted)]">{product.review_count} reviews</div>
                  </div>
                  <div className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-3 py-1 text-sm font-semibold text-amber-700 dark:text-amber-300">
                    <Star className="h-4 w-4" />
                    {product.avg_rating}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section>
        <ChatPanel
          title="Admin AI Chatbot"
          description="Ask questions about revenue, stock, reviews, and restock priorities. Every answer is grounded in SQLite analytics."
          endpoint="admin"
          accent="slate"
          examples={[
            'What were the best-selling products?',
            'Which category generated the highest revenue?',
            'Show low stock products.',
            'What should I restock first?',
          ]}
        />
      </section>
    </div>
  );
}
