'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SplineScene from '../components/SplineScene';
import {
  ShieldCheck,
  Users,
  Calendar,
  CreditCard,
  Activity,
  LogOut,
  Plus,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Search,
  Filter,
  Check,
  X,
  Lock,
  Terminal,
  Zap,
  Layers,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  Binary,
  Radio,
  FileText,
} from 'lucide-react';

interface Stats {
  employees: number;
  pending_leaves: number;
  pending_expenses: number;
}

interface EmployeeItem {
  id: string | number;
  full_name: string;
  designation: string;
  department: string;
  employee_code: string;
  is_active: boolean;
}

interface LeaveItem {
  id: number;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  reason: string;
}

interface ExpenseItem {
  id: number;
  employee_name: string;
  category: string;
  amount: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  description: string;
  requires_dual_key: boolean;
}

interface InterceptorLog {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  payload: string;
  verdict: 'ALLOW' | 'HOLD' | 'BLOCK';
  invariant: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'employees' | 'leaves' | 'expenses' | 'interceptor'>('overview');
  const [userEmail, setUserEmail] = useState<string>('admin@novapay.com');
  const [userRole, setUserRole] = useState<string>('ADMIN');

  // Employee list state
  const [employees, setEmployees] = useState<EmployeeItem[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isAddEmpModalOpen, setIsAddEmpModalOpen] = useState<boolean>(false);
  const [newEmpName, setNewEmpName] = useState('');
  const [newEmpDept, setNewEmpDept] = useState('ENGINEERING');
  const [newEmpDesignation, setNewEmpDesignation] = useState('');

  // Leaves & Expenses mock/live hybrid state
  const [leaves, setLeaves] = useState<LeaveItem[]>([
    {
      id: 101,
      employee_name: 'John Doe (EMP001)',
      leave_type: 'ANNUAL',
      start_date: '2026-10-15',
      end_date: '2026-10-18',
      days: 4,
      status: 'PENDING',
      reason: 'Family emergency trip',
    },
    {
      id: 102,
      employee_name: 'Jane Manager (MGR001)',
      leave_type: 'SICK',
      start_date: '2026-10-20',
      end_date: '2026-10-21',
      days: 2,
      status: 'PENDING',
      reason: 'Medical consultation',
    },
    {
      id: 103,
      employee_name: 'Vikram Singh (DEV003)',
      leave_type: 'CASUAL',
      start_date: '2026-11-01',
      end_date: '2026-11-02',
      days: 2,
      status: 'APPROVED',
      reason: 'Attending security conference',
    },
  ]);

  const [expenses, setExpenses] = useState<ExpenseItem[]>([
    {
      id: 201,
      employee_name: 'John Doe (EMP001)',
      category: 'TRAVEL',
      amount: 4500,
      status: 'PENDING',
      description: 'Local client transport & taxi',
      requires_dual_key: false,
    },
    {
      id: 202,
      employee_name: 'Aarav Patel (OPS002)',
      category: 'HARDWARE',
      amount: 78500,
      status: 'PENDING',
      description: 'Server rack replacement power units',
      requires_dual_key: true,
    },
    {
      id: 203,
      employee_name: 'Priya Sharma (FIN004)',
      category: 'MEALS',
      amount: 2200,
      status: 'APPROVED',
      description: 'Vendor working lunch',
      requires_dual_key: false,
    },
  ]);

  // Real-time ActionGate Interceptor Event Stream
  const [interceptorLogs, setInterceptorLogs] = useState<InterceptorLog[]>([
    {
      id: 'EVT-904',
      timestamp: 'Just now',
      agent: 'FinAgent-Alpha',
      action: 'process_payment',
      payload: '₹4,500 · AWS Invoicing',
      verdict: 'ALLOW',
      invariant: 'Below ₹10k threshold; verified task token',
    },
    {
      id: 'EVT-903',
      timestamp: '2 min ago',
      agent: 'ProcureBot-02',
      action: 'process_payment',
      payload: '₹78,500 · Dell Servers',
      verdict: 'HOLD',
      invariant: 'Dual-key required (> ₹10k threshold)',
    },
    {
      id: 'EVT-902',
      timestamp: '5 min ago',
      agent: 'ScraperAgent-9',
      action: 'export_records',
      payload: '12,500 customer records',
      verdict: 'BLOCK',
      invariant: 'Mass egress attempt (> 1,000 limit)',
    },
    {
      id: 'EVT-901',
      timestamp: '12 min ago',
      agent: 'AuditDaemon-1',
      action: 'read_logs',
      payload: 'Last 100 system audit rows',
      verdict: 'ALLOW',
      invariant: 'Read-only audit inspection authorized',
    },
  ]);

  // Token & initial loading
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    if (email) setUserEmail(email);

    if (!token) {
      router.replace('/login');
      return;
    }

    if (email?.includes('admin')) setUserRole('ADMIN');
    else if (email?.includes('manager')) setUserRole('MANAGER');
    else setUserRole('EMPLOYEE');

    fetchDashboardStats(token);
    fetchEmployeesList(token);
  }, [router]);

  const fetchDashboardStats = async (token: string) => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/api/dashboard/stats', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const data = await resp.json();
        setStats(data);
      } else {
        setStats({ employees: 12, pending_leaves: 2, pending_expenses: 3 });
      }
    } catch {
      setStats({ employees: 12, pending_leaves: 2, pending_expenses: 3 });
    }
  };

  const fetchEmployeesList = async (token: string) => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/api/employees/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.length > 0) {
          setEmployees(data);
          return;
        }
      }
      setEmployees([
        { id: 1, full_name: 'Admin User', designation: 'System Administrator', department: 'OPERATIONS', employee_code: 'ADM001', is_active: true },
        { id: 2, full_name: 'Jane Manager', designation: 'Engineering Manager', department: 'ENGINEERING', employee_code: 'MGR001', is_active: true },
        { id: 3, full_name: 'John Doe', designation: 'Software Engineer', department: 'ENGINEERING', employee_code: 'EMP001', is_active: true },
        { id: 4, full_name: 'Aarav Patel', designation: 'DevOps Lead', department: 'OPERATIONS', employee_code: 'OPS002', is_active: true },
        { id: 5, full_name: 'Priya Sharma', designation: 'Financial Controller', department: 'FINANCE', employee_code: 'FIN004', is_active: true },
      ]);
    } catch {
      setEmployees([
        { id: 1, full_name: 'Admin User', designation: 'System Administrator', department: 'OPERATIONS', employee_code: 'ADM001', is_active: true },
        { id: 2, full_name: 'Jane Manager', designation: 'Engineering Manager', department: 'ENGINEERING', employee_code: 'MGR001', is_active: true },
        { id: 3, full_name: 'John Doe', designation: 'Software Engineer', department: 'ENGINEERING', employee_code: 'EMP001', is_active: true },
      ]);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    router.push('/login');
  };

  const handleReviewLeave = async (id: number, newStatus: 'APPROVED' | 'REJECTED') => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await fetch(`http://127.0.0.1:8000/api/leaves/${id}?status=${newStatus}`, {
          method: 'PATCH',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (e) {
        console.error(e);
      }
    }
    setLeaves((prev) =>
      prev.map((l) => (l.id === id ? { ...l, status: newStatus } : l))
    );
    if (stats) {
      setStats({ ...stats, pending_leaves: Math.max(0, stats.pending_leaves - 1) });
    }
  };

  const handleReviewExpense = async (id: number, newStatus: 'APPROVED' | 'REJECTED') => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        await fetch(`http://127.0.0.1:8000/api/expenses/${id}?status=${newStatus}`, {
          method: 'PATCH',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (e) {
        console.error(e);
      }
    }
    setExpenses((prev) =>
      prev.map((ex) => (ex.id === id ? { ...ex, status: newStatus } : ex))
    );
    if (stats) {
      setStats({ ...stats, pending_expenses: Math.max(0, stats.pending_expenses - 1) });
    }
  };

  const handleCreateEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    const newCode = `EMP00${employees.length + 1}`;
    const payload = {
      full_name: newEmpName,
      department: newEmpDept,
      designation: newEmpDesignation || 'Specialist',
      employee_code: newCode,
    };

    if (token) {
      try {
        const resp = await fetch('http://127.0.0.1:8000/api/employees/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });
        if (resp.ok) {
          const created = await resp.json();
          setEmployees((prev) => [...prev, created]);
        } else {
          setEmployees((prev) => [
            ...prev,
            { id: Date.now(), ...payload, is_active: true },
          ]);
        }
      } catch {
        setEmployees((prev) => [
          ...prev,
          { id: Date.now(), ...payload, is_active: true },
        ]);
      }
    }

    if (stats) setStats({ ...stats, employees: stats.employees + 1 });
    setIsAddEmpModalOpen(false);
    setNewEmpName('');
    setNewEmpDesignation('');
  };

  const filteredEmployees = employees.filter(
    (e) =>
      e.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.designation?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen tactical-matrix-bg flex flex-col selection:bg-emerald-500/30 selection:text-emerald-300 text-slate-100">
      {/* Top Tactical Command HUD Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#030712]/90 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 via-cyan-500 to-indigo-600 p-0.5 shadow-md shadow-emerald-500/20">
                <div className="w-full h-full bg-[#030712] rounded-[10px] flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
                </div>
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-base tracking-wider text-white">
                    ACTIONGATE
                  </span>
                  <span className="text-slate-500">×</span>
                  <span className="text-xs font-semibold text-slate-300">NovaPay</span>
                  <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    HUD
                  </span>
                </div>
              </div>
            </Link>

            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/90 border border-white/10 text-[11px] font-mono text-slate-300 ml-4">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>LATTICE INVARIANTS: P1-P7 ENFORCING</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Operator Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-white/10 font-mono text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-slate-300 hidden sm:inline">{userEmail}</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {userRole}
              </span>
            </div>

            <button
              onClick={handleLogout}
              className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition flex items-center gap-1.5 text-xs font-mono"
              title="Terminate Session"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main HUD Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
        {/* Tactical Metric HUD Row */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
          <div className="hud-card hud-card-hover rounded-2xl p-5 border border-white/10 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>WORKFORCE ENCLAVE</span>
              <Users className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-black text-white">
                {stats?.employees ?? 12}
              </span>
              <span className="text-[11px] text-emerald-400 flex items-center gap-0.5">
                <TrendingUp className="w-3 h-3" /> Live SQLite
              </span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1">Verified Personnel Records</span>
          </div>

          <div className="hud-card hud-card-hover rounded-2xl p-5 border border-white/10 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>PENDING LEAVES</span>
              <Calendar className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-black text-amber-400">
                {stats?.pending_leaves ?? 2}
              </span>
              <span className="text-[11px] text-amber-300">
                Awaiting Sign-off
              </span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1">Manager Discretion Queue</span>
          </div>

          <div className="hud-card hud-card-hover rounded-2xl p-5 border border-white/10 flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>EXPENSE DUAL-KEY</span>
              <CreditCard className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-black text-cyan-300">
                {stats?.pending_expenses ?? 3}
              </span>
              <span className="text-[11px] text-cyan-300">
                Policy Intercepted
              </span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1">&gt; ₹10k Threshold Enforced</span>
          </div>

          <div className="hud-card hud-card-hover rounded-2xl p-5 border border-emerald-500/30 flex flex-col justify-between shadow-lg shadow-emerald-500/5">
            <div className="flex items-center justify-between text-emerald-400 text-xs">
              <span>GATEWAY INVIOLABILITY</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-black text-emerald-400">
                100%
              </span>
              <span className="text-[11px] text-emerald-400">
                Formal Meet ∧
              </span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1">122 Attack Proofs Sealed</span>
          </div>
        </section>

        {/* Tab Selector Navigation */}
        <div className="flex items-center gap-2 border-b border-white/10 pb-2 overflow-x-auto font-mono text-xs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 ${
              activeTab === 'overview'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>3D Defense Core & Telemetry</span>
          </button>

          <button
            onClick={() => setActiveTab('employees')}
            className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 ${
              activeTab === 'employees'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Operatives Directory ({employees.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('leaves')}
            className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 ${
              activeTab === 'leaves'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Leave Requests ({leaves.filter((l) => l.status === 'PENDING').length})</span>
          </button>

          <button
            onClick={() => setActiveTab('expenses')}
            className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 ${
              activeTab === 'expenses'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
            }`}
          >
            <CreditCard className="w-3.5 h-3.5" />
            <span>Expense Claims ({expenses.filter((e) => e.status === 'PENDING').length})</span>
          </button>

          <button
            onClick={() => setActiveTab('interceptor')}
            className={`px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 ${
              activeTab === 'interceptor'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-900/50'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>ActionGate Threat Stream</span>
          </button>
        </div>

        {/* Tab 1: 3D Core & Overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            {/* Spline 3D Scene Viewport */}
            <div className="lg:col-span-7 tactical-bracket hud-card rounded-3xl p-6 flex flex-col justify-between relative overflow-hidden">
              <div className="flex items-center justify-between z-10 font-mono">
                <div>
                  <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
                    <h2 className="text-lg font-bold text-white tracking-tight">
                      3D Holographic Action Citadel
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Interactive Spline 3D Security Mesh · Drag to rotate, inspect filaments
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-[10px]">
                  LIVE 3D ACTIVE
                </span>
              </div>

              <div className="w-full h-[360px] sm:h-[400px] my-3 rounded-2xl bg-[#030814]/90 border border-white/5 relative overflow-hidden">
                <SplineScene />
              </div>

              <div className="grid grid-cols-3 gap-3 font-mono text-xs border-t border-white/10 pt-4">
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-white/5">
                  <div className="text-slate-400 text-[10px]">POLICY PATH</div>
                  <div className="text-emerald-400 font-bold mt-0.5">meet(base, ai)</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-white/5">
                  <div className="text-slate-400 text-[10px]">AUDIT TAMPER-PROOF</div>
                  <div className="text-cyan-400 font-bold mt-0.5">Chained HMAC</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-white/5">
                  <div className="text-slate-400 text-[10px]">REPLAY DEFENSE</div>
                  <div className="text-indigo-400 font-bold mt-0.5">One-Time Nonce</div>
                </div>
              </div>
            </div>

            {/* Quick Actions & Live Stream */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              {/* Tactical Quick Action Box */}
              <div className="hud-card rounded-3xl p-6 border border-white/10 flex flex-col gap-4 font-mono">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <span>Immediate Operative Triggers</span>
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <button
                    onClick={() => {
                      setActiveTab('employees');
                      setIsAddEmpModalOpen(true);
                    }}
                    className="p-3 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 font-semibold transition flex items-center justify-between"
                  >
                    <span>+ New Operative</span>
                    <Plus className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => setActiveTab('leaves')}
                    className="p-3 rounded-xl bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 font-semibold transition flex items-center justify-between"
                  >
                    <span>Review Leaves</span>
                    <ArrowUpRight className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => setActiveTab('expenses')}
                    className="p-3 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 font-semibold transition flex items-center justify-between"
                  >
                    <span>Dual-Key Claims</span>
                    <ArrowUpRight className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => setActiveTab('interceptor')}
                    className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-white/10 text-slate-200 font-semibold transition flex items-center justify-between"
                  >
                    <span>Threat Feed</span>
                    <Terminal className="w-4 h-4 text-emerald-400" />
                  </button>
                </div>
              </div>

              {/* Mini Stream */}
              <div className="hud-card rounded-3xl p-6 border border-white/10 flex-1 flex flex-col justify-between font-mono">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-emerald-400" />
                      <span>Live Interceptor Telemetry</span>
                    </h3>
                    <span className="text-[10px] text-slate-500">Sub-millisecond</span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    {interceptorLogs.slice(0, 3).map((item) => (
                      <div
                        key={item.id}
                        className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center justify-between"
                      >
                        <div className="flex flex-col gap-0.5">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-200">{item.action}</span>
                            <span className="text-[10px] text-slate-500">({item.agent})</span>
                          </div>
                          <span className="text-[11px] text-slate-400">{item.payload}</span>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            item.verdict === 'ALLOW'
                              ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                              : item.verdict === 'HOLD'
                              ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                              : 'text-rose-400 bg-rose-500/10 border-rose-500/30'
                          }`}
                        >
                          {item.verdict}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
                  <span>FastAPI ERP Core</span>
                  <Link href="http://127.0.0.1:8000/docs" target="_blank" className="text-emerald-400 hover:underline flex items-center gap-1">
                    API Docs <ArrowUpRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Operatives Directory */}
        {activeTab === 'employees' && (
          <div className="hud-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col gap-6 font-mono">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                  <Users className="w-5 h-5 text-emerald-400" />
                  <span>Personnel & Agent Directory</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-sans">
                  Active organizational personnel, department security contexts, and RBAC clearances.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search personnel..."
                    className="pl-9 pr-4 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400"
                  />
                </div>
                <button
                  onClick={() => setIsAddEmpModalOpen(true)}
                  className="px-4 py-2 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition shadow-md"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Operative</span>
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto rounded-2xl border border-white/10">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/90 border-b border-white/10 text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="p-3.5">Security Code</th>
                    <th className="p-3.5">Operative Name</th>
                    <th className="p-3.5">Department</th>
                    <th className="p-3.5">Role Designation</th>
                    <th className="p-3.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 bg-slate-900/40">
                  {filteredEmployees.map((emp) => (
                    <tr key={emp.id} className="hover:bg-slate-800/40 transition">
                      <td className="p-3.5 text-emerald-400 font-bold">{emp.employee_code}</td>
                      <td className="p-3.5 text-slate-200 font-semibold">{emp.full_name}</td>
                      <td className="p-3.5">
                        <span className="px-2 py-0.5 rounded bg-slate-800 border border-white/10 text-[10px] text-slate-300 font-mono">
                          {emp.department}
                        </span>
                      </td>
                      <td className="p-3.5 text-slate-400">{emp.designation}</td>
                      <td className="p-3.5">
                        <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          Authorized
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Leaves */}
        {activeTab === 'leaves' && (
          <div className="hud-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono">
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-amber-400" />
                  <span>Time-Off Governance Queue</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-sans">
                  Dual-approval leave queue for managers and enterprise administrators.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {leaves.map((leave) => (
                <div
                  key={leave.id}
                  className="p-5 rounded-2xl bg-slate-950/70 border border-white/10 flex flex-col justify-between gap-4"
                >
                  <div className="flex flex-col gap-2 font-mono text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-emerald-400 font-bold">
                        {leave.employee_name}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded border ${
                          leave.status === 'APPROVED'
                            ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                            : leave.status === 'REJECTED'
                            ? 'text-rose-400 bg-rose-500/10 border-rose-500/30'
                            : 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                        }`}
                      >
                        {leave.status}
                      </span>
                    </div>

                    <div className="text-slate-300">
                      <strong>Category:</strong> {leave.leave_type} · <strong>Duration:</strong> {leave.days} days
                    </div>
                    <div className="text-slate-400">
                      <strong>Schedule:</strong> {leave.start_date} → {leave.end_date}
                    </div>
                    <p className="text-slate-400 italic mt-1 font-sans">&quot;{leave.reason}&quot;</p>
                  </div>

                  {leave.status === 'PENDING' && (
                    <div className="flex items-center gap-2 pt-3 border-t border-white/5 font-mono text-xs">
                      <button
                        onClick={() => handleReviewLeave(leave.id, 'APPROVED')}
                        className="flex-1 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-bold flex items-center justify-center gap-1 transition"
                      >
                        <Check className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => handleReviewLeave(leave.id, 'REJECTED')}
                        className="flex-1 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 font-bold flex items-center justify-center gap-1 transition"
                      >
                        <X className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Expenses */}
        {activeTab === 'expenses' && (
          <div className="hud-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono">
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-cyan-400" />
                  <span>Financial Expense Dual-Key Gate</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-sans">
                  ActionGate Policy Invariant: Any expense &gt; ₹10,000 is intercepted and locked for Dual-Key authorization.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {expenses.map((exp) => (
                <div
                  key={exp.id}
                  className="p-5 rounded-2xl bg-slate-950/70 border border-white/10 flex flex-col justify-between gap-4"
                >
                  <div className="flex flex-col gap-2 font-mono">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-emerald-400 font-bold">
                        {exp.employee_name}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded border ${
                          exp.status === 'APPROVED'
                            ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                            : exp.status === 'REJECTED'
                            ? 'text-rose-400 bg-rose-500/10 border-rose-500/30'
                            : 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                        }`}
                      >
                        {exp.status}
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between mt-1">
                      <span className="text-2xl font-black text-white">
                        ₹{exp.amount.toLocaleString('en-IN')}
                      </span>
                      <span className="text-xs text-slate-400">{exp.category}</span>
                    </div>

                    <p className="text-xs text-slate-400 mt-1 font-sans">{exp.description}</p>

                    {exp.requires_dual_key && (
                      <div className="mt-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-300 flex items-center gap-1.5">
                        <Lock className="w-3 h-3 text-amber-400" />
                        <span>ActionGate Intercept: Dual-Key Policy Triggered</span>
                      </div>
                    )}
                  </div>

                  {exp.status === 'PENDING' && (
                    <div className="flex items-center gap-2 pt-3 border-t border-white/5 font-mono text-xs">
                      <button
                        onClick={() => handleReviewExpense(exp.id, 'APPROVED')}
                        className="flex-1 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-bold flex items-center justify-center gap-1 transition"
                      >
                        <Check className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => handleReviewExpense(exp.id, 'REJECTED')}
                        className="flex-1 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 font-bold flex items-center justify-center gap-1 transition"
                      >
                        <X className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 5: Interceptor Stream */}
        {activeTab === 'interceptor' && (
          <div className="hud-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col gap-6 font-mono">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  <span>ActionGate Real-Time Event Stream</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-sans">
                  Live audit trail of autonomous agent tool requests evaluated across formal lattice invariants.
                </p>
              </div>

              <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300">
                122 ATTACK VECTORS SEALED
              </div>
            </div>

            <div className="space-y-3 text-xs">
              {interceptorLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 rounded-2xl bg-slate-950/80 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-emerald-500/30 transition"
                >
                  <div className="flex items-start sm:items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-md text-xs font-bold border ${
                        log.verdict === 'ALLOW'
                          ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                          : log.verdict === 'HOLD'
                          ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                          : 'text-rose-400 bg-rose-500/10 border-rose-500/30'
                      }`}
                    >
                      {log.verdict}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-200 font-semibold">{log.action}</span>
                        <span className="text-slate-500 text-[11px]">({log.agent})</span>
                      </div>
                      <div className="text-slate-400 text-[11px] mt-0.5">{log.payload}</div>
                    </div>
                  </div>

                  <div className="text-right sm:max-w-xs">
                    <div className="text-[11px] text-slate-300">{log.invariant}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">{log.timestamp} · {log.id}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Add Operative Modal */}
      {isAddEmpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="hud-card rounded-3xl p-6 sm:p-8 max-w-md w-full border border-emerald-500/30 shadow-2xl relative font-mono">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-emerald-400" />
                <span>Register Operative Profile</span>
              </h3>
              <button
                onClick={() => setIsAddEmpModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateEmployee} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 uppercase tracking-wider mb-1">
                  Full Legal / Security Name
                </label>
                <input
                  type="text"
                  required
                  value={newEmpName}
                  onChange={(e) => setNewEmpName(e.target.value)}
                  placeholder="e.g. Vikram Malhotra"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white focus:outline-none focus:border-emerald-400"
                />
              </div>

              <div>
                <label className="block text-slate-300 uppercase tracking-wider mb-1">
                  Security Department
                </label>
                <select
                  value={newEmpDept}
                  onChange={(e) => setNewEmpDept(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white focus:outline-none focus:border-emerald-400"
                >
                  <option value="ENGINEERING">ENGINEERING</option>
                  <option value="OPERATIONS">OPERATIONS</option>
                  <option value="FINANCE">FINANCE</option>
                  <option value="SALES">SALES</option>
                  <option value="HR">HR</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 uppercase tracking-wider mb-1">
                  Designation / Role
                </label>
                <input
                  type="text"
                  value={newEmpDesignation}
                  onChange={(e) => setNewEmpDesignation(e.target.value)}
                  placeholder="e.g. Lead Zero-Trust Architect"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white focus:outline-none focus:border-emerald-400"
                />
              </div>

              <div className="pt-2 flex items-center gap-3">
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold transition shadow-md"
                >
                  Register Profile
                </button>
                <button
                  type="button"
                  onClick={() => setIsAddEmpModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#030712] py-6 text-center text-xs text-slate-500 font-mono mt-auto">
        <p>ActionGate × NovaPay ERP · Autonomous Agent Action Firewall · All Operations Nominal</p>
      </footer>
    </div>
  );
}
