import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getProduct } from '../lib/api';
import type { ProductDetail } from '../lib/types';
import { ProductCard } from '../components/ProductCard';

function currency(value: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

export function ProductPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getProduct(Number(productId))
      .then((data) => {
        if (active) setProduct(data);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [productId]);

  if (loading) {
    return <div className="glass h-[700px] animate-pulse rounded-[2rem]" />;
  }

  if (!product) {
    return (
      <div className="glass rounded-[2rem] p-8">
        <h1 className="text-3xl font-display font-bold">Product not found</h1>
        <Link to="/" className="mt-4 inline-flex rounded-full bg-accent-600 px-4 py-2 text-sm font-semibold text-white">
          Back to home
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-10">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Product details</div>
          <h1 className="mt-2 text-4xl font-display font-bold">{product.name}</h1>
        </div>
        <Link to="/" className="glass rounded-full px-4 py-2 text-sm font-semibold">
          Back to catalog
        </Link>
      </div>

      <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="glass overflow-hidden rounded-[2rem] p-4 shadow-lg shadow-black/5">
          <div className="overflow-hidden rounded-[1.5rem] bg-gradient-to-br from-[#f4efe3] to-[#dce7df] dark:from-slate-900 dark:to-slate-800">
            <img src={product.image} alt={product.name} className="h-full w-full object-cover" />
          </div>
        </div>
        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-accent-600 px-3 py-1 text-xs font-semibold text-white">{product.category}</span>
            <span className="rounded-full bg-slate-900/5 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-white/10 dark:text-slate-200">{product.brand}</span>
          </div>
          <div className="mt-4 text-4xl font-display font-bold">{currency(product.price)}</div>
          <div className="mt-2 text-sm text-[var(--muted)]">Rating {product.rating.toFixed(1)} · {product.stock} units in stock</div>
          <p className="mt-5 text-base leading-7 text-[var(--muted)]">{product.description}</p>
          <div className="mt-6">
            <h2 className="text-xl font-display font-bold">Specifications</h2>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              {product.features.map((feature) => (
                <div key={feature} className="rounded-2xl bg-slate-900/5 px-4 py-3 text-sm font-medium dark:bg-white/10">
                  {feature}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Reviews</div>
            <h2 className="mt-2 text-2xl font-display font-bold">Recent customer feedback</h2>
          </div>
          <div className="space-y-3">
            {product.reviews.map((review) => (
              <div key={review.id} className="rounded-2xl border border-[var(--border)] bg-white/60 p-4 dark:bg-white/5">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold">{review.rating.toFixed(1)} / 5</div>
                  <div className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Verified review</div>
                </div>
                <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{review.comment}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-[2rem] p-6 shadow-lg shadow-black/5">
          <div className="mb-4">
            <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Related products</div>
            <h2 className="mt-2 text-2xl font-display font-bold">Similar items in this category</h2>
          </div>
          <div className="space-y-4">
            {product.related_products.map((related) => (
              <ProductCard key={related.id} product={related} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
