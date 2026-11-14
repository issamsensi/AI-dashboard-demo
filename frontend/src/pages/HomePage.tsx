import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Filter, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getProducts } from '../lib/api';
import type { Product } from '../lib/types';
import { ProductCard } from '../components/ProductCard';

const heroStats = [
  { label: 'Products', value: '50+' },
  { label: 'AI tools', value: '9' },
  { label: 'Live SQLite data', value: '1 source of truth' },
];

export function HomePage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setLoading(true);
      try {
        const data = await getProducts({ search: search || undefined, category: category || undefined, limit: 18 });
        setProducts(data);
      } finally {
        setLoading(false);
      }
    }, 180);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [search, category]);

  const categories = useMemo(() => Array.from(new Set(products.map((product) => product.category))), [products]);

  return (
    <div className="space-y-10 pb-10">
      <section className="relative overflow-hidden rounded-[2.5rem] border border-[var(--border)] bg-[color:var(--bg-elevated)] p-8 shadow-xl shadow-black/5 sm:p-10 lg:p-14">
        <div className="absolute inset-0 soft-grid opacity-30" />
        <div className="relative grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6 animate-rise">
            <div className="inline-flex items-center gap-2 rounded-full bg-accent-600 px-4 py-2 text-sm font-semibold text-white shadow-glow">
              <SparklesIcon />
              AI-powered e-commerce demo
            </div>
            <div className="space-y-4">
              <h1 className="max-w-3xl text-5xl font-display font-bold tracking-tight text-balance sm:text-6xl">
                A realistic storefront where AI is grounded in SQLite.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-[var(--muted)]">
                Explore products, compare specs, ask the shopping assistant for budget-friendly options, and inspect the dashboard used to demo AI over structured business data.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {heroStats.map((stat) => (
                <div key={stat.label} className="glass rounded-3xl px-4 py-4">
                  <div className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">{stat.label}</div>
                  <div className="mt-2 text-lg font-display font-bold">{stat.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-[2rem] p-5 shadow-glow animate-rise">
            <div className="space-y-4 rounded-[1.6rem] bg-slate-900 p-6 text-white dark:bg-white dark:text-slate-900">
              <div className="text-sm font-semibold uppercase tracking-[0.24em] text-white/65 dark:text-slate-500">Featured use cases</div>
              <div className="space-y-4">
                <div className="rounded-2xl bg-white/10 p-4 dark:bg-slate-900/5">
                  <div className="font-semibold">Customer chat</div>
                  <p className="mt-1 text-sm leading-6 text-white/75 dark:text-slate-600">Search products, compare options, and stay within budget without hallucinations.</p>
                </div>
                <div className="rounded-2xl bg-white/10 p-4 dark:bg-slate-900/5">
                  <div className="font-semibold">Admin intelligence</div>
                  <p className="mt-1 text-sm leading-6 text-white/75 dark:text-slate-600">Ask about revenue, low stock, bad reviews, and restock priorities.</p>
                </div>
                <div className="rounded-2xl bg-white/10 p-4 dark:bg-slate-900/5">
                  <div className="font-semibold">Fast extension path</div>
                  <p className="mt-1 text-sm leading-6 text-white/75 dark:text-slate-600">Ready for Shopify, PostgreSQL, Stripe, auth, vectors, and real analytics later.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Catalog</div>
            <h2 className="mt-2 text-3xl font-display font-bold">Search featured products</h2>
          </div>
          <div className="glass flex w-full max-w-2xl items-center gap-3 rounded-2xl px-4 py-3">
            <Search className="h-5 w-5 text-[var(--muted)]" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search laptops, cameras, gaming gear, and more"
              className="w-full bg-transparent text-sm outline-none placeholder:text-[var(--muted)]"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setCategory('')}
            className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
              !category ? 'bg-accent-600 text-white' : 'glass hover:-translate-y-0.5'
            }`}
          >
            <Filter className="h-4 w-4" />
            All categories
          </button>
          {categories.map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => setCategory(value)}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                category === value ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'glass hover:-translate-y-0.5'
              }`}
            >
              {value}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="glass h-96 animate-pulse rounded-3xl" />
            ))}
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        {[
          ['AI-first', 'The assistant only uses SQLite-backed tool calls.'],
          ['Beautiful cards', 'Every product, metric, and answer is shown in a polished card layout.'],
          ['Easy to extend', 'Swap in Shopify, PostgreSQL, vector stores, auth, or payments later.'],
        ].map(([title, description]) => (
          <div key={title} className="glass rounded-3xl p-6">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">{title}</div>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{description}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

function SparklesIcon() {
  return <ArrowRight className="h-4 w-4" />;
}
