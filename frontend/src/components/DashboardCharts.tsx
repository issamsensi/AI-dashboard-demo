import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const palette = ['#1f7a6b', '#d9c9a8', '#114e45', '#3f7f76', '#7aa99f', '#2f3a3a'];

export function DashboardCharts({
  salesByMonth,
  revenueByCategory,
  topProducts,
  stockLevels,
}: {
  salesByMonth: Array<{ month: string; revenue: number; orders: number }>;
  revenueByCategory: Array<{ category: string; revenue: number }>;
  topProducts: Array<{ id: number; name: string; revenue: number; units_sold: number }>;
  stockLevels: Array<{ id: number; name: string; category: string; stock: number; rating: number; brand: string; price: number }>;
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <div className="glass rounded-[2rem] p-5 shadow-lg shadow-black/5">
        <div className="mb-4">
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Sales by month</div>
          <h3 className="mt-1 text-2xl font-display font-bold">Revenue trend</h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={salesByMonth}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="revenue" stroke="#1f7a6b" strokeWidth={3} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="orders" stroke="#d9c9a8" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass rounded-[2rem] p-5 shadow-lg shadow-black/5">
        <div className="mb-4">
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Revenue by category</div>
          <h3 className="mt-1 text-2xl font-display font-bold">Business mix</h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={revenueByCategory}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="category" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="revenue" radius={[10, 10, 0, 0]}>
                {revenueByCategory.map((entry, index) => (
                  <Cell key={entry.category} fill={palette[index % palette.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass rounded-[2rem] p-5 shadow-lg shadow-black/5">
        <div className="mb-4">
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Top products</div>
          <h3 className="mt-1 text-2xl font-display font-bold">Revenue leaders</h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topProducts} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="revenue" radius={[0, 12, 12, 0]}>
                {topProducts.map((entry, index) => (
                  <Cell key={entry.name} fill={palette[index % palette.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass rounded-[2rem] p-5 shadow-lg shadow-black/5">
        <div className="mb-4">
          <div className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">Stock levels</div>
          <h3 className="mt-1 text-2xl font-display font-bold">Low-stock pressure</h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stockLevels.slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="stock" radius={[0, 12, 12, 0]} fill="#1f7a6b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
