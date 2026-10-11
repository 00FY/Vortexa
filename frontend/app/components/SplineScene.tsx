'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { ShieldAlert, Compass, Maximize2, RotateCw } from 'lucide-react';

// Dynamic import with SSR disabled
const Spline = dynamic(() => import('@splinetool/react-spline'), {
  ssr: false,
  loading: () => <SplineLoadingSkeleton />,
});

function SplineLoadingSkeleton() {
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center min-h-[360px] bg-[#050a16] rounded-2xl border border-emerald-500/20 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.12)_0,transparent_70%)] animate-pulse" />
      <div className="relative z-10 flex flex-col items-center gap-3">
        <div className="w-14 h-14 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin" />
        <span className="text-[11px] uppercase tracking-widest text-emerald-400 font-mono">
          CALIBRATING 3D ACTION CORE...
        </span>
      </div>
    </div>
  );
}

// Ultra-refined interactive 3D particle filament globe
function CanvasCyberFallback({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 550);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 450);

    const onResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', onResize);

    const NUM_PARTICLES = 180;
    const particles: { theta: number; phi: number; radius: number; speed: number; hue: number }[] = [];
    for (let i = 0; i < NUM_PARTICLES; i++) {
      particles.push({
        theta: Math.random() * Math.PI * 2,
        phi: Math.acos(Math.random() * 2 - 1),
        radius: Math.min(width, height) * 0.35,
        speed: 0.0025 + Math.random() * 0.0035,
        hue: Math.random() > 0.4 ? 160 : 190, // emerald or cyan
      });
    }

    let rotationAngle = 0;
    let mouseX = 0;
    let mouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / width - 0.5) * 2;
      mouseY = ((e.clientY - rect.top) / height - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      rotationAngle += 0.005;
      const targetAngleY = rotationAngle + mouseX * 0.7;
      const targetAngleX = mouseY * 0.5;

      const projected: { x: number; y: number; z: number; alpha: number; hue: number }[] = [];

      particles.forEach((p) => {
        p.theta += p.speed;
        const x3d = p.radius * Math.sin(p.phi) * Math.cos(p.theta);
        const y3d = p.radius * Math.sin(p.phi) * Math.sin(p.theta);
        const z3d = p.radius * Math.cos(p.phi);

        const cosY = Math.cos(targetAngleY);
        const sinY = Math.sin(targetAngleY);
        const xRotY = x3d * cosY - z3d * sinY;
        const zRotY = x3d * sinY + z3d * cosY;

        const cosX = Math.cos(targetAngleX);
        const sinX = Math.sin(targetAngleX);
        const yRotX = y3d * cosX - zRotY * sinX;
        const zRotX = y3d * sinX + zRotY * cosX;

        const fov = 420;
        const scale = fov / (fov + zRotX);
        const x2d = width / 2 + xRotY * scale;
        const y2d = height / 2 + yRotX * scale;
        const alpha = Math.max(0.12, Math.min(1, (zRotX + p.radius) / (2 * p.radius)));

        projected.push({ x: x2d, y: y2d, z: zRotX, alpha, hue: p.hue });
      });

      // Neural filament connections
      ctx.lineWidth = 0.8;
      for (let i = 0; i < projected.length; i++) {
        for (let j = i + 1; j < projected.length; j++) {
          const dx = projected[i].x - projected[j].x;
          const dy = projected[i].y - projected[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 46) {
            const filamentAlpha = 0.28 * (1 - dist / 46) * projected[i].alpha;
            ctx.strokeStyle = `rgba(16, 185, 129, ${filamentAlpha})`;
            ctx.beginPath();
            ctx.moveTo(projected[i].x, projected[i].y);
            ctx.lineTo(projected[j].x, projected[j].y);
            ctx.stroke();
          }
        }
      }

      // Render quantum nodes
      projected.forEach((p) => {
        const radius = Math.max(1.2, 2.8 * p.alpha);
        ctx.fillStyle =
          p.hue === 160
            ? `rgba(16, 232, 150, ${p.alpha})`
            : `rgba(6, 182, 212, ${p.alpha * 0.9})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
      });

      // Center core glow
      const gradient = ctx.createRadialGradient(
        width / 2,
        height / 2,
        8,
        width / 2,
        height / 2,
        Math.min(width, height) * 0.36
      );
      gradient.addColorStop(0, 'rgba(16, 185, 129, 0.18)');
      gradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.09)');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, Math.min(width, height) * 0.36, 0, Math.PI * 2);
      ctx.fill();

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className={`relative w-full h-full min-h-[360px] overflow-hidden rounded-2xl bg-[#030814] ${className || ''}`}>
      <canvas ref={canvasRef} className="w-full h-full block cursor-grab active:cursor-grabbing" />
      <div className="absolute top-3 left-3 px-2 py-0.5 rounded bg-black/60 border border-emerald-500/20 text-[9px] font-mono text-emerald-400 backdrop-blur-md">
        SYS.CORE: 3D ACTION MATRIX · ACTIVE
      </div>
      <div className="absolute bottom-3 right-3 px-2.5 py-1 rounded-full bg-slate-900/80 border border-emerald-500/30 text-[10px] font-mono text-emerald-300 flex items-center gap-1.5 shadow-lg backdrop-blur-md">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
        Interactive Holo-Mesh · 60 FPS
      </div>
    </div>
  );
}

interface SplineSceneProps {
  sceneUrl?: string;
  className?: string;
}

export default function SplineScene({
  sceneUrl = 'https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode',
  className = '',
}: SplineSceneProps) {
  const [loadState, setLoadState] = useState<'loading' | 'success' | 'failed'>('loading');

  useEffect(() => {
    // 8-second safety fallback if external Spline CDN is delayed
    const timer = setTimeout(() => {
      if (loadState === 'loading') {
        setLoadState('failed');
      }
    }, 8000);

    return () => clearTimeout(timer);
  }, [loadState]);

  return (
    <div className={`relative w-full h-full flex items-center justify-center overflow-hidden ${className}`}>
      {loadState === 'failed' ? (
        <CanvasCyberFallback />
      ) : (
        <div className="w-full h-full relative">
          <Spline
            scene={sceneUrl}
            onLoad={() => setLoadState('success')}
            onError={() => setLoadState('failed')}
            className="w-full h-full"
          />
          {loadState === 'loading' && (
            <div className="absolute inset-0 z-10 pointer-events-none">
              <SplineLoadingSkeleton />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
