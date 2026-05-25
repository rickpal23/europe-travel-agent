import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Travel Points Planner",
  description: "Build your ideal trip and redeem points for maximum value.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <style>{`
          @keyframes shimmer {
            0%   { background-position: -600px 0; }
            100% { background-position: 600px 0; }
          }
          @keyframes gradientDrift {
            0%, 100% { background-position: 0% 50%; }
            50%       { background-position: 100% 50%; }
          }
          @keyframes chipIn {
            0%   { transform: scale(0.55) translateY(4px); opacity: 0; }
            65%  { transform: scale(1.07) translateY(-1px); opacity: 1; }
            100% { transform: scale(1) translateY(0); opacity: 1; }
          }
          @keyframes stopSlide {
            from { opacity: 0; transform: translateX(-10px); }
            to   { opacity: 1; transform: translateX(0); }
          }
          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
          }
          .shimmer {
            background: linear-gradient(90deg, #f1f1f3 0%, #e5e5e8 45%, #f1f1f3 90%);
            background-size: 1200px 100%;
            animation: shimmer 1.6s ease-in-out infinite;
          }
          .hero-gradient {
            background: linear-gradient(135deg, #18181b 0%, #1e1b4b 40%, #18181b 70%, #0f172a 100%);
            background-size: 250% 250%;
            animation: gradientDrift 14s ease infinite;
          }
          .chip-spring {
            animation: chipIn 0.26s cubic-bezier(0.34, 1.56, 0.64, 1) both;
          }
          .stop-slide {
            animation: stopSlide 0.45s ease both;
          }
          .fade-up {
            animation: fadeUp 0.35s ease both;
          }
        `}</style>
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
