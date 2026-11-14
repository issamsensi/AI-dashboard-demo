import { BadgeIndianRupee, ShoppingCart } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Product } from '../lib/types';

function currency(value: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

export function ProductCard({ product }: { product: Product }) {
  return (
    <Link
      to={`/products/${product.id}`}
      className="group glass animate-rise overflow-hidden rounded-3xl p-4 shadow-lg shadow-black/5 transition duration-300 hover:-translate-y-1 hover:shadow-glow"
    >
      <div className="relative mb-4 overflow-hidden rounded-2xl bg-gradient-to-br from-[#f4efe3] to-[#dce7df] dark:from-slate-900 dark:to-slate-800">
        <img
          src={product.image}
          alt={product.name}
          className="h-44 w-full object-cover transition duration-500 group-hover:scale-105"
        />
        <div className="absolute left-3 top-3 rounded-full bg-white/85 px-3 py-1 text-xs font-semibold text-slate-900 backdrop-blur">
          {product.category}
        </div>
      </div>
      <div className="space-y-3">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">{product.brand}</div>
          <h3 className="mt-1 text-xl font-display font-bold leading-tight">{product.name}</h3>
        </div>
        <p className="line-clamp-2 text-sm leading-6 text-[var(--muted)]">{product.description}</p>
        <div className="flex flex-wrap gap-2">
          {product.features.slice(0, 3).map((feature) => (
            <span key={feature} className="rounded-full bg-slate-900/5 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-white/10 dark:text-slate-200">
              {feature}
            </span>
          ))}
        </div>
        <div className="flex items-center justify-between pt-2">
          <div>
            <div className="text-2xl font-bold tracking-tight">{currency(product.price)}</div>
            <div className="text-sm text-[var(--muted)]">Rating {product.rating.toFixed(1)} · {product.stock} left</div>
          </div>
          <div className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-accent-600 text-white transition group-hover:scale-105">
            <ShoppingCart className="h-5 w-5" />
          </div>
        </div>
      </div>
    </Link>
  );
}
