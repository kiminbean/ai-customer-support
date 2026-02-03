"use client";

import { useState } from "react";
import Link from "next/link";
import { LogoIcon } from "@/components/icons";
import { useI18n, LanguageSwitcher } from "@/lib/i18n";

interface NavbarProps {
  variant?: "landing" | "app";
  activePage?: string;
}

export function Navbar({ variant = "landing", activePage }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { t } = useI18n();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
              <LogoIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">SupportAI</span>
          </Link>
          
          {/* Desktop Navigation */}
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
          
          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-3">
            <LanguageSwitcher className="border-gray-200 text-gray-600" />
            <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900 transition-colors hidden sm:block">
              {t("nav.login")}
            </Link>
            <Link
              href="/demo"
              className="px-4 py-2 bg-[#2563EB] text-white text-sm font-medium rounded-lg hover:bg-[#1d4ed8] transition-colors shadow-sm"
            >
              {t("nav.signup")}
            </Link>
          </div>

          {/* Mobile Hamburger Button */}
          <div className="flex md:hidden">
            <button
              type="button"
              className="text-gray-600 hover:text-gray-900 p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="space-y-1 px-4 py-6">
            {variant === "landing" && (
              <>
                <a 
                  href="#features" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="block py-3 text-base font-medium text-gray-600 hover:text-gray-900 border-b border-gray-50"
                >
                  기능
                </a>
                <a 
                  href="#pricing" 
                  onClick={() => setMobileMenuOpen(false)}
                  className="block py-3 text-base font-medium text-gray-600 hover:text-gray-900 border-b border-gray-50"
                >
                  요금제
                </a>
              </>
            )}
            <Link 
              href="/demo"
              onClick={() => setMobileMenuOpen(false)} 
              className={`block py-3 text-base font-medium border-b border-gray-50 ${activePage === 'demo' ? 'text-[#2563EB]' : 'text-gray-600 hover:text-gray-900'}`}
            >
              데모
            </Link>
            <Link 
              href="/dashboard" 
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-3 text-base font-medium border-b border-gray-50 ${activePage === 'dashboard' ? 'text-[#2563EB]' : 'text-gray-600 hover:text-gray-900'}`}
            >
              대시보드
            </Link>
            <Link 
              href="/datahub" 
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-3 text-base font-medium border-b border-gray-50 ${activePage === 'datahub' ? 'text-[#2563EB]' : 'text-gray-600 hover:text-gray-900'}`}
            >
              데이터 허브
            </Link>
            <Link 
              href="/crawler" 
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-3 text-base font-medium border-b border-gray-50 ${activePage === 'crawler' ? 'text-[#2563EB]' : 'text-gray-600 hover:text-gray-900'}`}
            >
              웹 크롤러
            </Link>
            
            <div className="pt-6 space-y-3">
              <Link 
                href="/dashboard" 
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full text-center py-3 text-base font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                로그인
              </Link>
              <Link
                href="/demo"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full text-center py-3 bg-[#2563EB] text-white text-base font-medium rounded-lg hover:bg-[#1d4ed8] shadow-sm"
              >
                무료 시작하기
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
