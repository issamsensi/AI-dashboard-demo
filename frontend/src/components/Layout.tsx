import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';

export function Layout() {
  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100">
      <Navbar />
      <main className="section-shell pb-16 pt-6 sm:pt-10">
        <Outlet />
      </main>
    </div>
  );
}
