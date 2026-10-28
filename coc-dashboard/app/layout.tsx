import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const clash = localFont({
  src: "./fonts/Clash-Regular.otf",
  // Only one weight exists and it is already heavy; cover the full range so
  // font-bold/semibold use it as-is instead of a smeared synthetic bold.
  weight: "100 900",
  variable: "--font-clash",
});

export const metadata: Metadata = {
  title: "Clash of Clans Dashboard",
  description: "Comprehensive clan analysis and player statistics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${clash.variable} antialiased bg-slate-950 text-white`}>
        {children}
      </body>
    </html>
  );
}
