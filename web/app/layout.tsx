import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Travel Points Planner",
  description: "Plan your Europe trip using points and miles",
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
