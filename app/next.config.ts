import type { NextConfig } from "next";
import path from "path";

const appDir = path.resolve(__dirname);

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    root: appDir,
  },
  
  // 이미지 최적화 설정
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30일 캐시
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  // 성능 최적화
  poweredByHeader: false, // X-Powered-By 헤더 제거
  compress: true, // gzip 압축 활성화
  
  // 실험적 기능
  experimental: {
    optimizePackageImports: [
      'react-icons',
      'lodash',
      'date-fns',
    ],
  },
  
  // 보안 헤더
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
      // 정적 자원 캐싱
      {
        source: "/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },
  
  // 번들 분석 (필요시 활성화)
  // bundlePagesRouterDependencies: true,
};

export default nextConfig;
