'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import with SSR disabled to prevent Next.js hydration issues
const Spline = dynamic(() => import('@splinetool/react-spline'), {
  ssr: false,
  loading: () => <SplineLoadingSkeleton />,
});

function SplineLoadingSkeleton() {
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center min-h-[350px] bg-slate-950/40 rounded-2xl border border-cyan-500/20 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,240,255,0.12)_0,transparent_70%)] animate-pulse" />
      <div className="relative z-10 flex flex-col items-center gap-3">
        <div className="w-16 h-16 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
        <span className="text-xs uppercase tracking-widest text-cyan-400 font-mono">
          Initializing 3D Neural Gate...
        </span>
      </div>
    </div>
  );
}

// Canvas-based interactive 3D particle sphere fallback
function CanvasCyberFallback({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 500);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 450);

    const onResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', onResize);

    // Particle nodes on a 3D sphere
    const NUM_PARTICLES = 160;
    const particles: { theta: number; phi: number; radius: number; speed: number }[] = [];
    for (let i = 0; i < NUM_PARTICLES; i++) {
      particles.push({
        theta: Math.random() * Math.PI * 2,
        phi: Math.acos(Math.random() * 2 - 1),
        radius: Math.min(width, height) * 0.32,
        speed: 0.003 + Math.random() * 0.004,
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

      rotationAngle += 0.006;
      const targetAngleY = rotationAngle + mouseX * 0.8;
      const targetAngleX = mouseY * 0.5;

      const projected: { x: number; y: number; z: number; alpha: number }[] = [];

      particles.forEach((p) => {
        p.theta += p.speed;
        const x3d = p.radius * Math.sin(p.phi) * Math.cos(p.theta);
        const y3d = p.radius * Math.sin(p.phi) * Math.sin(p.theta);
        const z3d = p.radius * Math.cos(p.phi);

        // Rotate Y
        const cosY = Math.cos(targetAngleY);
        const sinY = Math.sin(targetAngleY);
        const xRotY = x3d * cosY - z3d * sinY;
        const zRotY = x3d * sinY + z3d * cosY;

        // Rotate X
        const cosX = Math.cos(targetAngleX);
        const sinX = Math.sin(targetAngleX);
        const yRotX = y3d * cosX - zRotY * sinX;
        const zRotX = y3d * sinX + zRotY * cosX;

        // Projection
        const fov = 400;
        const scale = fov / (fov + zRotX);
        const x2d = width / 2 + xRotY * scale;
        const y2d = height / 2 + yRotX * scale;
        const alpha = Math.max(0.15, Math.min(1, (zRotX + p.radius) / (2 * p.radius)));

        projected.push({ x: x2d, y: y2d, z: zRotX, alpha });
      });

      // Draw connecting lines between near nodes
      ctx.lineWidth = 0.75;
      for (let i = 0; i < projected.length; i++) {
        for (let j = i + 1; j < projected.length; j++) {
          const dx = projected[i].x - projected[j].x;
          const dy = projected[i].y - projected[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 48) {
            ctx.strokeStyle = `rgba(0, 240, 255, ${0.25 * (1 - dist / 48) * projected[i].alpha})`;
            ctx.beginPath();
            ctx.moveTo(projected[i].x, projected[i].y);
            ctx.lineTo(projected[j].x, projected[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      projected.forEach((p) => {
        const radius = Math.max(1.2, 2.5 * p.alpha);
        ctx.fillStyle = p.z > 0 ? `rgba(0, 240, 255, ${p.alpha})` : `rgba(121, 40, 202, ${p.alpha * 0.8})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
      });

      // Core glow in center
      const gradient = ctx.createRadialGradient(
        width / 2,
        height / 2,
        10,
        width / 2,
        height / 2,
        Math.min(width, height) * 0.35
      );
      gradient.addColorStop(0, 'rgba(0, 240, 255, 0.15)');
      gradient.addColorStop(0.5, 'rgba(121, 40, 202, 0.08)');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, Math.min(width, height) * 0.35, 0, Math.PI * 2);
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
    <div className={`relative w-full h-full min-h-[350px] overflow-hidden rounded-2xl ${className || ''}`}>
      <canvas ref={canvasRef} className="w-full h-full block" />
      <div className="absolute bottom-3 right-4 px-2.5 py-1 rounded-full bg-slate-900/80 border border-cyan-500/30 text-[10px] font-mono text-cyan-300 flex items-center gap-1.5 shadow-lg backdrop-blur-md">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
        Interactive Neural Sphere · ActionGate 3D
      </div>
    </div>
  );
}

interface SplineSceneProps {
  sceneUrl?: string;
  className?: string;
  interactive?: boolean;
}

export default function SplineScene({
  sceneUrl = 'https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode',
  className = '',
}: SplineSceneProps) {
  const [loadState, setLoadState] = useState<'loading' | 'success' | 'failed'>('loading');

  useEffect(() => {
    // If Spline CDN takes longer than 9 seconds, gracefully transition to custom 3D Canvas
    const timer = setTimeout(() => {
      if (loadState === 'loading') {
        setLoadState('failed');
      }
    }, 9000);

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
