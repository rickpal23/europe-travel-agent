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
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
