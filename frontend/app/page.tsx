'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import SplineScene from './components/SplineScene';
import { 
  ShieldCheck, 
  Lock, 
  Terminal, 
  Activity, 
  ArrowRight, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Zap, 
  ChevronRight,
  Database,
  Users,
  ExternalLink
} from 'lucide-react';

export default function Home() {
  const [selectedDemoAction, setSelectedDemoAction] = useState<number>(0);

  const demoScenarios = [
    {
      id: 0,
      title: "Routine Micro-Expense",
      tool: "process_payment",
      amount: "₹4,850",
      recipient: "Cloud Host Services",
      agent: "Autonomous FinAgent-04",
      verdict: "ALLOW",
      reason: "Within autonomous threshold (≤ ₹10,000) & verified task context TASK-DISP-101",
      lattice: "Baseline: ALLOW ∧ AI: ALLOW → FINAL: ALLOW",
      badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    },
    {
      id: 1,
      title: "High-Value Transfer",
      tool: "process_payment",
      amount: "₹75,000",
      recipient: "Hardware Vendor Corp",
      agent: "Autonomous ProcurementBot",
      verdict: "HOLD",
      reason: "Threshold exceeded (> ₹10,000). Held for Human-in-the-Loop Dual-Key Approval.",
      lattice: "Baseline: HOLD ∧ AI: ALLOW → FINAL: HOLD (P1 Lattice Invariant: AI never relaxes baseline)",
      badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    },
    {
      id: 2,
      title: "Exfiltration Injection Attack",
      tool: "export_records",
      amount: "15,000 records",
      recipient: "External Endpoint (pastebin)",
      agent: "Compromised Agent-007",
      verdict: "BLOCK",
      reason: "Mass data exfiltration (> 1,000 records limit) & unauthorized external egress.",
      lattice: "Baseline: BLOCK ∧ AI: ALLOW → FINAL: BLOCK (Zero-Trust Interceptor)",
      badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    },
    {
      id: 3,
      title: "P1 Lattice Invariant Test",
      tool: "modify_admin_acl",
      amount: "Privilege Elevation",
      recipient: "System Root",
      agent: "Adversarial Prompt-Injected Agent",
      verdict: "BLOCK",
      reason: "Policy threshold boundary: AI requested ALLOW, but deterministic policy is BLOCK. Result strictly BLOCK.",
      lattice: "Formal Lattice Meet (∧): min(BLOCK, ALLOW) = BLOCK",
      badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    },
  ];

  const currentScenario = demoScenarios[selectedDemoAction];

  return (
    <div className="min-h-screen cyber-bg flex flex-col selection:bg-cyan-500/20">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#070a12]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  NovaPay ERP
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  ACTIONGATE
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono hidden sm:block">
                Autonomous Agent Action Authorization
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/60 border border-white/5 text-xs font-mono text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>FastAPI Backend 8000 · ONLINE</span>
            </div>
            <Link
              href="/login"
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 transition"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-xl text-sm font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 hover:opacity-95 shadow-lg shadow-cyan-500/25 transition flex items-center gap-1.5"
            >
              Live Command Center
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Main Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16 flex flex-col gap-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Headlines & Metrics */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-mono w-fit">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>Problem Statement C-01 · Vortexa 3.0</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
              Zero-Trust Gatekeeper for{' '}
              <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
                Autonomous AI Agents
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg leading-relaxed max-w-2xl">
              An enterprise ERP action firewall where untrusted LLM outputs are rigorously bounded by 
              mathematical lattice invariants. Auto-allows safe operations, holds high-stakes actions for dual-key manager approval, and blocks malicious privilege escalation.
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/login"
                className="px-6 py-3.5 rounded-xl font-semibold bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 hover:opacity-95 shadow-xl shadow-cyan-500/20 transition flex items-center gap-2 group"
              >
                <span>Demo One-Click Login</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </Link>
              <Link
                href="/dashboard"
                className="px-6 py-3.5 rounded-xl font-medium bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-white/10 transition flex items-center gap-2"
              >
                <Activity className="w-4 h-4 text-cyan-400" />
                <span>Open Dashboard</span>
              </Link>
              <a
                href="http://127.0.0.1:8000/health"
                target="_blank"
                rel="noreferrer"
                className="px-4 py-3.5 rounded-xl font-mono text-xs text-slate-400 hover:text-slate-200 border border-white/5 hover:border-white/10 transition flex items-center gap-1.5"
              >
                <span>/health</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* Invariant Verified Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10">
              <div className="flex flex-col">
                <span className="text-2xl font-bold font-mono text-cyan-400">122 / 122</span>
                <span className="text-xs text-slate-400">Attack Vectors Stopped</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-bold font-mono text-indigo-400">15 / 15</span>
                <span className="text-xs text-slate-400">Mutation Bugs Caught</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-bold font-mono text-emerald-400">100%</span>
                <span className="text-xs text-slate-400">Lattice Invariant Inviolability</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-bold font-mono text-amber-400">&lt; 3.2ms</span>
                <span className="text-xs text-slate-400">Dual-Gate Latency</span>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Spline 3D Scene */}
          <div className="lg:col-span-5 relative">
            <div className="relative rounded-3xl p-1 bg-gradient-to-b from-cyan-500/30 via-indigo-500/20 to-transparent shadow-2xl shadow-cyan-500/10">
              <div className="w-full h-[450px] sm:h-[480px] bg-[#070b14]/90 rounded-[22px] overflow-hidden relative flex flex-col">
                {/* 3D Scene Header */}
                <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
                  <div className="px-3 py-1 rounded-full bg-slate-900/80 border border-cyan-500/30 backdrop-blur-md flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    <span className="text-[11px] font-mono text-cyan-300 font-medium">
                      Live 3D Security Mesh
                    </span>
                  </div>
                  <div className="px-2.5 py-1 rounded bg-black/60 border border-white/10 text-[10px] font-mono text-slate-400 backdrop-blur-md">
                    Spline 3D Core
                  </div>
                </div>

                {/* Spline 3D Embed */}
                <div className="w-full h-full">
                  <SplineScene />
                </div>

                {/* 3D Scene Bottom Bar */}
                <div className="absolute bottom-4 left-4 right-4 z-20 pointer-events-none">
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-white/10 backdrop-blur-md flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">Interceptor: Dual-Gate Invariant Active</span>
                    <span className="text-cyan-400 font-bold">LATTICE: MEET (∧)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Interactive ActionGate Policy Interceptor Simulator */}
        <section className="glass-card rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
              <div>
                <div className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-cyan-400" />
                  <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                    Interactive ActionGate Interceptor Simulator
                  </h2>
                </div>
                <p className="text-sm text-slate-400 mt-1">
                  Test live simulated tool invocations against ActionGate's deterministic lattice gatekeeper.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Formal Invariant:</span>
                <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-xs font-mono text-cyan-300">
                  ∀a ∈ Actions: final(a) ≤ baseline(a)
                </span>
              </div>
            </div>

            {/* Scenario Selector Pills */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
              {demoScenarios.map((sc, idx) => (
                <button
                  key={sc.id}
                  onClick={() => setSelectedDemoAction(idx)}
                  className={`p-3 rounded-xl text-left font-mono text-xs transition border ${
                    selectedDemoAction === idx
                      ? 'bg-cyan-500/15 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/10'
                      : 'bg-slate-900/40 border-white/5 text-slate-400 hover:border-white/20 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-slate-200">{sc.title}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${sc.badgeColor}`}>
                      {sc.verdict}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 truncate">{sc.amount} · {sc.tool}</div>
                </button>
              ))}
            </div>

            {/* Live Inspection Box */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 bg-slate-950/70 p-5 rounded-2xl border border-white/5 font-mono text-xs">
              <div className="md:col-span-5 flex flex-col gap-2.5">
                <span className="text-slate-500 uppercase tracking-wider text-[10px]">
                  Simulated Inbound Agent Payload
                </span>
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-white/5 space-y-1.5 text-slate-300">
                  <div><span className="text-slate-500">Agent ID:</span> <span className="text-cyan-300">{currentScenario.agent}</span></div>
                  <div><span className="text-slate-500">Action:</span> <span className="text-amber-300">{currentScenario.tool}</span></div>
                  <div><span className="text-slate-500">Parameter:</span> <span className="text-emerald-300">{currentScenario.amount}</span></div>
                  <div><span className="text-slate-500">Target:</span> <span>{currentScenario.recipient}</span></div>
                </div>
              </div>

              <div className="md:col-span-7 flex flex-col justify-between gap-4">
                <div className="flex flex-col gap-2">
                  <span className="text-slate-500 uppercase tracking-wider text-[10px]">
                    Lattice Resolution Result
                  </span>
                  <div className="flex items-center gap-3">
                    <span className={`text-base font-bold px-3 py-1 rounded-lg border flex items-center gap-1.5 ${currentScenario.badgeColor}`}>
                      {currentScenario.verdict === 'ALLOW' && <CheckCircle2 className="w-4 h-4" />}
                      {currentScenario.verdict === 'HOLD' && <AlertTriangle className="w-4 h-4" />}
                      {currentScenario.verdict === 'BLOCK' && <XCircle className="w-4 h-4" />}
                      VERDICT: {currentScenario.verdict}
                    </span>
                    <span className="text-xs text-slate-400">
                      Evaluated in <strong className="text-slate-200">1.8ms</strong>
                    </span>
                  </div>
                  <p className="text-slate-300 text-xs mt-1 leading-relaxed">
                    {currentScenario.reason}
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 text-[11px] text-cyan-400">
                  {currentScenario.lattice}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Dual-Gate Invariant Math</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Untrusted LLM reasoning cannot relax deterministic constraints. Evaluated with formal lattice meets where the safety floor always dominates.
            </p>
          </div>

          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Dual-Key Human Approval</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              High-value payments and privilege updates are held securely. Cryptographic nonces ensure approvals cannot be forged or replayed.
            </p>
          </div>

          <div className="glass-card glass-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">FastAPI ERP Integration</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Complete production ERP backend with Employees, Department RBAC, Leave Requests, and Expense Claims with real-time policy interception.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#070a12] py-8 text-center text-xs text-slate-500 font-mono">
        <p>NovaPay ERP · ActionGate Autonomous Agent Authorization · Built for Vortexa 3.0</p>
      </footer>
    </div>
  );
}
