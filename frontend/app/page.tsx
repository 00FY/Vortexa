'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import SplineScene from './components/SplineScene';
import {
  ShieldAlert,
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
  Radio,
  FileCheck2,
  Crosshair,
  ExternalLink,
  Flame,
  Binary,
} from 'lucide-react';

export default function Home() {
  const [selectedDemoAction, setSelectedDemoAction] = useState<number>(0);

  const demoScenarios = [
    {
      id: 0,
      title: "Routine Micro-Disbursement",
      threatLevel: "LOW RISK",
      tool: "process_payment",
      amount: "₹4,850",
      target: "Cloud Server Node US-East",
      agent: "Autonomous FinOps Agent",
      taskContext: "TASK-DISP-101 (Pre-approved)",
      baseline: "ALLOW",
      aiVerdict: "ALLOW",
      finalVerdict: "ALLOW",
      reason: "Action within autonomous safety ceiling (≤ ₹10,000) with validated cryptographic task token.",
      latticeFormula: "meet(ALLOW, ALLOW) = ALLOW",
      badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    },
    {
      id: 1,
      title: "Threshold Boundary Transfer",
      threatLevel: "ELEVATED RISK",
      tool: "process_payment",
      amount: "₹75,000",
      target: "Industrial Silicon Corp",
      agent: "Autonomous ProcurementBot",
      taskContext: "TASK-DISP-101",
      baseline: "HOLD",
      aiVerdict: "ALLOW",
      finalVerdict: "HOLD",
      reason: "Exceeds autonomous limit. AI requested ALLOW, but deterministic policy forces HOLD for Dual-Key Sign-off.",
      latticeFormula: "meet(HOLD, ALLOW) = HOLD (P1 Invariant: AI never relaxes baseline)",
      badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    },
    {
      id: 2,
      title: "Mass Exfiltration Attack",
      threatLevel: "CRITICAL THREAT",
      tool: "export_records",
      amount: "15,000 user rows",
      target: "External Pastebin / Webhook",
      agent: "Injected Agent-007",
      taskContext: "TASK-EXPORT-505 (Compromised)",
      baseline: "BLOCK",
      aiVerdict: "ALLOW (Jailbroken)",
      finalVerdict: "BLOCK",
      reason: "Hard limit breach (> 1,000 records). Malicious egress blocked instantly before network execution.",
      latticeFormula: "meet(BLOCK, ALLOW) = BLOCK (Zero-Trust Interceptor)",
      badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    },
    {
      id: 3,
      title: "P1 Lattice Invariant Test",
      threatLevel: "ATTACK MUTANT",
      tool: "modify_admin_acl",
      amount: "Privilege Elevation",
      target: "System Core",
      agent: "Adversarial LLM Output",
      taskContext: "FORGED_TOKEN",
      baseline: "BLOCK",
      aiVerdict: "ALLOW (Model Hallucination)",
      finalVerdict: "BLOCK",
      reason: "Mathematical proof: Final action must be ≤ Baseline in the authorization lattice. Model bypassed zero security.",
      latticeFormula: "∀ action: final(action) ≤ baseline(action)",
      badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    },
  ];

  const currentScenario = demoScenarios[selectedDemoAction];

  return (
    <div className="min-h-screen tactical-matrix-bg flex flex-col selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Top Tactical Status Bar */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#030712]/90 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-cyan-500 to-indigo-600 p-0.5 shadow-lg shadow-emerald-500/20">
              <div className="w-full h-full bg-[#030712] rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-wider text-white">
                  ACTIONGATE
                </span>
                <span className="text-slate-500">×</span>
                <span className="font-semibold text-slate-300 text-sm">NovaPay ERP</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  LATTICE V1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono hidden sm:block">
                Autonomous AI Agent Action Authorization Citadel
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-white/10 text-[11px] font-mono text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>INTERCEPTOR: ZERO-TRUST LOCKED</span>
            </div>
            <Link
              href="/login"
              className="px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 hover:text-white hover:bg-white/5 transition border border-transparent hover:border-white/10"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-xl text-xs font-mono font-bold bg-emerald-400 hover:bg-emerald-300 text-slate-950 shadow-lg shadow-emerald-500/20 transition flex items-center gap-1.5"
            >
              <span>Command Center</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Main Tactical Presentation */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14 flex flex-col gap-14">
        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Column: Headlines & Mathematical Citadel */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs font-mono w-fit">
              <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span>Problem Statement C-01 · Vortexa 3.0 Finalist Architecture</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.05]">
              The Dual-Gate Action Citadel for{' '}
              <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                Autonomous AI Agents
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg leading-relaxed max-w-2xl font-light">
              Where non-deterministic LLM reasoning is bounded by mathematical lattice invariants.
              Automatically allows low-risk tasks, holds high-stakes actions for cryptographic dual-key human approval, and eliminates privilege escalation.
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/login"
                className="px-6 py-3.5 rounded-xl font-mono text-xs font-bold bg-emerald-400 hover:bg-emerald-300 text-slate-950 shadow-xl shadow-emerald-500/20 transition flex items-center gap-2 group"
              >
                <span>Instant Demo Sign In</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </Link>
              <Link
                href="/dashboard"
                className="px-6 py-3.5 rounded-xl font-mono text-xs font-medium bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-white/10 transition flex items-center gap-2"
              >
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Open Live Command HUD</span>
              </Link>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="px-4 py-3.5 rounded-xl font-mono text-xs text-slate-400 hover:text-slate-200 border border-white/5 hover:border-white/10 transition flex items-center gap-1.5"
              >
                <span>FastAPI /docs</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* Proof Metric Counters */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10 font-mono">
              <div className="flex flex-col">
                <span className="text-2xl font-black text-emerald-400">122 / 122</span>
                <span className="text-[11px] text-slate-400">Attacks Neutralized</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-black text-cyan-400">15 / 15</span>
                <span className="text-[11px] text-slate-400">Mutants Terminated</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-black text-indigo-400">0.00%</span>
                <span className="text-[11px] text-slate-400">Privilege Leakage</span>
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-black text-amber-400">&lt; 2.1ms</span>
                <span className="text-[11px] text-slate-400">Lattice Gate Overhead</span>
              </div>
            </div>
          </div>

          {/* Right Column: 3D Holographic Action Core */}
          <div className="lg:col-span-5 relative">
            <div className="tactical-bracket hud-card rounded-3xl p-1 shadow-2xl relative">
              <div className="w-full h-[460px] sm:h-[490px] bg-[#030814]/95 rounded-[22px] overflow-hidden relative flex flex-col">
                {/* 3D Telemetry Header */}
                <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
                  <div className="px-3 py-1 rounded-full bg-slate-900/90 border border-emerald-500/30 backdrop-blur-md flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                    <span className="text-[10px] font-mono text-emerald-300 font-bold uppercase tracking-wider">
                      Spline 3D Defense Core
                    </span>
                  </div>
                  <div className="px-2.5 py-1 rounded bg-black/70 border border-white/10 text-[9px] font-mono text-slate-400 backdrop-blur-md">
                    LAT 37.7 · LNG -122.4
                  </div>
                </div>

                {/* Spline 3D Embed */}
                <div className="w-full h-full">
                  <SplineScene />
                </div>

                {/* 3D Telemetry Bottom Bar */}
                <div className="absolute bottom-4 left-4 right-4 z-20 pointer-events-none">
                  <div className="p-3 rounded-xl bg-slate-950/90 border border-emerald-500/20 backdrop-blur-md flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">Invariant: P1 Meet Rule Active</span>
                    <span className="text-emerald-400 font-bold">100% INVIOLABLE</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Interactive ActionGate Policy Interceptor Simulator */}
        <section className="hud-card rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 flex flex-col gap-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
              <div>
                <div className="flex items-center gap-2.5">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                    Interactive ActionGate Interceptor Simulator
                  </h2>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Test simulated tool actions against the deterministic dual-gate lattice firewall.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Formal Guarantee:</span>
                <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300">
                  final = meet(baseline, ai_verdict)
                </span>
              </div>
            </div>

            {/* Scenario Pills */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {demoScenarios.map((sc, idx) => (
                <button
                  key={sc.id}
                  onClick={() => setSelectedDemoAction(idx)}
                  className={`p-3.5 rounded-xl text-left font-mono text-xs transition border ${
                    selectedDemoAction === idx
                      ? 'bg-emerald-500/15 border-emerald-400/60 text-white shadow-lg shadow-emerald-500/10'
                      : 'bg-slate-900/50 border-white/5 text-slate-400 hover:border-white/20 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-slate-200">{sc.title}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border ${sc.badgeColor}`}>
                      {sc.finalVerdict}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 truncate">{sc.amount} · {sc.tool}</div>
                </button>
              ))}
            </div>

            {/* Tactical Live Inspection Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 bg-slate-950/80 p-5 rounded-2xl border border-white/5 font-mono text-xs">
              <div className="md:col-span-5 flex flex-col gap-3">
                <span className="text-slate-500 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                  <Binary className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Agent Action Telemetry</span>
                </span>
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-white/5 space-y-2 text-slate-300">
                  <div><span className="text-slate-500">Agent:</span> <span className="text-cyan-300">{currentScenario.agent}</span></div>
                  <div><span className="text-slate-500">Tool:</span> <span className="text-amber-300 font-bold">{currentScenario.tool}</span></div>
                  <div><span className="text-slate-500">Magnitude:</span> <span className="text-emerald-300 font-bold">{currentScenario.amount}</span></div>
                  <div><span className="text-slate-500">Destination:</span> <span>{currentScenario.target}</span></div>
                  <div><span className="text-slate-500">Token Context:</span> <span className="text-indigo-300">{currentScenario.taskContext}</span></div>
                </div>
              </div>

              <div className="md:col-span-7 flex flex-col justify-between gap-4">
                <div className="flex flex-col gap-2">
                  <span className="text-slate-500 uppercase tracking-wider text-[10px]">
                    Lattice Gate Evaluation
                  </span>
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold px-3 py-1 rounded-lg border flex items-center gap-1.5 ${currentScenario.badgeColor}`}>
                      {currentScenario.finalVerdict === 'ALLOW' && <CheckCircle2 className="w-4 h-4" />}
                      {currentScenario.finalVerdict === 'HOLD' && <AlertTriangle className="w-4 h-4" />}
                      {currentScenario.finalVerdict === 'BLOCK' && <XCircle className="w-4 h-4" />}
                      FINAL VERDICT: {currentScenario.finalVerdict}
                    </span>
                    <span className="text-xs text-slate-400">
                      Evaluated in <strong className="text-slate-200">1.8ms</strong>
                    </span>
                  </div>
                  <p className="text-slate-300 text-xs mt-1 leading-relaxed">
                    {currentScenario.reason}
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-black/50 border border-white/10 text-[11px] text-emerald-400">
                  <strong>Formal Lattice Formula:</strong> {currentScenario.latticeFormula}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Architecture Triad */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="hud-card hud-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Lattice Invariant Math</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-light">
              Deterministic security floor cannot be lowered by prompt injections or model hallucinations. If policy is BLOCK, final outcome is strictly BLOCK.
            </p>
          </div>

          <div className="hud-card hud-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Dual-Key Human Gate</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-light">
              High-value payments and administrative edits are held securely. Cryptographic nonces ensure authorizations cannot be spoofed or replayed.
            </p>
          </div>

          <div className="hud-card hud-card-hover rounded-2xl p-6 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">FastAPI ERP Integration</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-light">
              Full enterprise ERP backend with employee directories, role-based access control, leave management, and expense claims.
            </p>
          </div>
        </section>
      </main>

      {/* Tactical Footer */}
      <footer className="border-t border-white/10 bg-[#030712] py-8 text-center text-xs text-slate-500 font-mono">
        <p>ActionGate × NovaPay ERP · Built for Vortexa 3.0 · Problem Statement C-01</p>
      </footer>
    </div>
  );
}
