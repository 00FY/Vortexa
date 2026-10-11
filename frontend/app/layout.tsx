import type { Metadata } from "next";
import { Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ActionGate × NovaPay ERP · Autonomous Agent Action Firewall",
  description: "Tactical Zero-Trust Action Authorization for Autonomous AI Agents · Dual-Gate Policy Lattice & Cryptographic Audit Core",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${jetbrainsMono.variable} dark h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#030712] text-slate-100 selection:bg-emerald-500/30 selection:text-emerald-300 font-sans">
        {children}
      </body>
    </html>
  );
}
