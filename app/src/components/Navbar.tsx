"use client";

import Link from "next/link";
import { LogoIcon } from "@/components/icons";

interface NavbarProps {
  variant?: "landing" | "app";
  activePage?: string;
}

export function Navbar({ variant = "landing", activePage }: NavbarProps) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
              <LogoIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">SupportAI</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            {variant === "landing" && (
              <>
                <a href="#features" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">기능</a>
                <a href="#pricing" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">요금제</a>
              </>
            )}
            <Link 
              href="/demo" 
              className={`text-sm transition-colors ${activePage === 'demo' ? 'text-[#2563EB] font-medium' : 'text-gray-600 hover:text-gray-900'}`}
            >
              데모
            </Link>
            <Link 
              href="/dashboard" 
              className={`text-sm transition-colors ${activePage === 'dashboard' ? 'text-[#2563EB] font-medium' : 'text-gray-600 hover:text-gray-900'}`}
            >
              대시보드
            </Link>
            <Link 
              href="/datahub" 
              className={`text-sm transition-colors ${activePage === 'datahub' ? 'text-[#2563EB] font-medium' : 'text-gray-600 hover:text-gray-900'}`}
            >
              데이터 허브
            </Link>
            <Link 
              href="/crawler" 
              className={`text-sm transition-colors ${activePage === 'crawler' ? 'text-[#2563EB] font-medium' : 'text-gray-600 hover:text-gray-900'}`}
            >
              웹 크롤러
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900 transition-colors hidden sm:block">
              로그인
            </Link>
            <Link
              href="/demo"
              className="px-4 py-2 bg-[#2563EB] text-white text-sm font-medium rounded-lg hover:bg-[#1d4ed8] transition-colors shadow-sm"
            >
              무료 시작하기
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
