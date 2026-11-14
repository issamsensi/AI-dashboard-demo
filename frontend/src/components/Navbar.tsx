import { useEffect, useState } from 'react';
import { Bot, LayoutDashboard, MoonStar, ShoppingBag, SunMedium } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(() => {
    const storedTheme = window.localStorage.getItem('ai-commerce-theme');
    if (storedTheme) {
      return storedTheme === 'dark';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    window.localStorage.setItem('ai-commerce-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  return (
    <button
      type="button"
      onClick={() => setDarkMode((value) => !value)}
      className="glass inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition hover:-translate-y-0.5"
    >
      {darkMode ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
      {darkMode ? 'Light' : 'Dark'}
    </button>
  );
}

export function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color:var(--bg-elevated)] backdrop-blur-xl">
      <div className="section-shell flex items-center justify-between gap-4 py-4">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-600 text-white shadow-glow">
            <ShoppingBag className="h-5 w-5" />
          </div>
          <div>
            <div className="font-display text-lg font-bold tracking-tight">Aster Cart AI</div>
            <div className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">Demo storefront</div>
          </div>
        </Link>

        <nav className="hidden items-center gap-2 md:flex">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                isActive ? 'bg-accent-600 text-white shadow-glow' : 'glass hover:-translate-y-0.5'
              }`
            }
          >
            <LayoutDashboard className="h-4 w-4" />
            Intelligent Dashboard
          </NavLink>
          <NavLink
            to="/assistant"
            className={({ isActive }) =>
              `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                isActive ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'glass hover:-translate-y-0.5'
              }`
            }
          >
            <Bot className="h-4 w-4" />
            AI Shopping Assistant
          </NavLink>
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <div className="md:hidden">
            <Link to="/dashboard" className="glass inline-flex rounded-full px-3 py-2 text-sm font-semibold">
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
