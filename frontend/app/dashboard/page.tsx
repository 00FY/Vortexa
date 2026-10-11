'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Stats {
  employees: number;
  pending_leaves: number;
  pending_expenses: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.replace('/login');
      return;
    }
    const fetchStats = async () => {
      try {
        const resp = await fetch('http://127.0.0.1:8000/api/dashboard/stats', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!resp.ok) {
          if (resp.status === 401) {
            // token invalid/expired
            localStorage.removeItem('access_token');
            router.replace('/login');
            return;
          }
          const data = await resp.json();
          throw new Error(data.detail || 'Failed to load stats');
        }
        const data = await resp.json();
        setStats(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchStats();
  }, [router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 p-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">
        Dashboard
      </h1>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded bg-white p-4 shadow dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Employees
          </h2>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {stats.employees}
          </p>
        </div>
        <div className="rounded bg-white p-4 shadow dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Pending Leaves
          </h2>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {stats.pending_leaves}
          </p>
        </div>
        <div className="rounded bg-white p-4 shadow dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Pending Expenses
          </h2>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
            {stats.pending_expenses}
          </p>
        </div>
      </div>
    </div>
  );
}
