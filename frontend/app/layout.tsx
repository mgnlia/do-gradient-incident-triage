import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Incident Triage | DigitalOcean Gradient",
  description: "AI-powered on-call incident triage assistant built on DigitalOcean Gradient™ AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0d1117]">{children}</body>
    </html>
  );
}
