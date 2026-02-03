import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/Providers";
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
  title: {
    default: "AI 고객지원 플랫폼 | SupportAI",
    template: "%s | SupportAI",
  },
  description: "AI 기반 고객지원 자동화 플랫폼. 24시간 자동 응답, 다국어 지원, 실시간 분석 대시보드를 제공합니다.",
  keywords: ["AI", "고객지원", "챗봇", "자동화", "고객센터", "CS", "SupportAI"],
  authors: [{ name: "SupportAI Team" }],
  creator: "SupportAI",
  publisher: "SupportAI",
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || "https://supportai.example.com"),
  openGraph: {
    type: "website",
    locale: "ko_KR",
    url: "/",
    siteName: "SupportAI",
    title: "AI 고객지원 플랫폼 | SupportAI",
    description: "AI 기반 고객지원 자동화 플랫폼. 24시간 자동 응답, 다국어 지원, 실시간 분석 대시보드를 제공합니다.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "SupportAI - AI 고객지원 플랫폼",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI 고객지원 플랫폼 | SupportAI",
    description: "AI 기반 고객지원 자동화 플랫폼. 24시간 자동 응답, 다국어 지원, 실시간 분석 대시보드를 제공합니다.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#2563EB",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const apiOrigin = new URL(apiUrl).origin;

  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href={apiOrigin} />
        <link rel="dns-prefetch" href={apiOrigin} />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
