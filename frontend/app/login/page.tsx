'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SplineScene from '../components/SplineScene';
import { ShieldCheck, Lock, User, Key, ArrowRight, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleQuickFill = (roleEmail: string, rolePass: string) => {
    setEmail(roleEmail);
    setPassword(rolePass);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const resp = await fetch('http://127.0.0.1:8000/api/users/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }).toString(),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.detail || 'Authentication failed. Please verify credentials.');
      }

      const { access_token } = await resp.json();
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_email', email);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen cyber-bg flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 selection:bg-cyan-500/20">
      {/* Top Bar Return Link */}
      <div className="max-w-6xl w-full mx-auto mb-6 flex items-center justify-between">
        <Link 
          href="/" 
          className="flex items-center gap-2 text-xs font-mono text-slate-400 hover:text-cyan-400 transition"
        >
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>← Return to Overview</span>
        </Link>
        <span className="text-[11px] font-mono text-slate-500">
          Backend: http://127.0.0.1:8000
        </span>
      </div>

      <div className="max-w-6xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* Left Side: 3D Visual & Architecture Core */}
        <div className="lg:col-span-7 glass-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col justify-between relative overflow-hidden">
          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-4">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>ActionGate Zero-Trust Layer</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Enterprise Identity & Action Perimeter
            </h2>
            <p className="text-sm text-slate-400 mt-2 max-w-lg leading-relaxed">
              Authenticate into NovaPay ERP. Every action taken by users or delegated AI agents is 
              evaluated through zero-trust lattice verification.
            </p>
          </div>

          {/* Interactive Spline Scene */}
          <div className="w-full h-[320px] sm:h-[360px] my-4 rounded-2xl overflow-hidden bg-slate-950/60 border border-white/5 relative">
            <SplineScene />
            <div className="absolute bottom-3 left-4 px-2.5 py-1 rounded bg-black/70 border border-white/10 text-[10px] font-mono text-cyan-400 backdrop-blur-md">
              SECURE SESSION CHANNEL · ENCRYPTED
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center font-mono text-xs border-t border-white/10 pt-4">
            <div className="p-2 rounded-xl bg-slate-900/40 border border-white/5">
              <div className="text-cyan-400 font-bold">RBAC</div>
              <div className="text-[10px] text-slate-500">Admin/Mgr/Emp</div>
            </div>
            <div className="p-2 rounded-xl bg-slate-900/40 border border-white/5">
              <div className="text-indigo-400 font-bold">DUAL-KEY</div>
              <div className="text-[10px] text-slate-500">Human Approval</div>
            </div>
            <div className="p-2 rounded-xl bg-slate-900/40 border border-white/5">
              <div className="text-emerald-400 font-bold">INVARIANTS</div>
              <div className="text-[10px] text-slate-500">Deterministic</div>
            </div>
          </div>
        </div>

        {/* Right Side: Sleek Glassmorphism Login Card */}
        <div className="lg:col-span-5 glass-card rounded-3xl p-6 sm:p-8 border border-white/10 flex flex-col justify-between shadow-2xl relative">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">System Sign In</h1>
                <p className="text-xs text-slate-400">Enter your credentials or choose a role</p>
              </div>
            </div>

            {/* Quick-Fill Role Selector for Evaluators & Judges */}
            <div className="mb-6 p-3 rounded-2xl bg-slate-950/60 border border-white/5">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-cyan-400" />
                <span>Instant Demo Role Fill:</span>
              </div>
              <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                <button
                  type="button"
                  onClick={() => handleQuickFill('admin@novapay.com', 'Admin@123')}
                  className="px-2.5 py-1.5 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-300 font-medium transition text-center"
                >
                  Admin
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('manager@example.com', 'manager123')}
                  className="px-2.5 py-1.5 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 font-medium transition text-center"
                >
                  Manager
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('employee@example.com', 'employee123')}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-white/10 text-slate-300 font-medium transition text-center"
                >
                  Employee
                </button>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-300 font-mono">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@novapay.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                    <Key className="w-4 h-4" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-2 py-3 rounded-xl font-semibold bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-500 text-slate-950 hover:opacity-95 shadow-xl shadow-cyan-500/20 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="w-5 h-5 rounded-full border-2 border-slate-950 border-t-transparent animate-spin" />
                ) : (
                  <>
                    <span>Authenticate Session</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 text-center text-xs text-slate-500">
            NovaPay Enterprise ERP · Protected by ActionGate
          </div>
        </div>
      </div>
    </div>
  );
}
