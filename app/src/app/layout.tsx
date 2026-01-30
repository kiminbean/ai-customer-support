import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI 고객지원 플랫폼 | SupportAI",
  description: "AI 기반 고객지원 자동화 플랫폼. 24시간 자동 응답, 다국어 지원, 실시간 분석 대시보드를 제공합니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const apiOrigin = new URL(apiUrl).origin;

  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href={apiOrigin} />
        <link rel="dns-prefetch" href={apiOrigin} />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
