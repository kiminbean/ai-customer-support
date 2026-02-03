"use client";

import Link from "next/link";
import {
  LogoIcon,
  DashboardIcon,
  DatabaseIcon,
  GlobeIcon,
  MicrophoneIcon,
  BookIcon,
} from "@/components/icons";
import { BackendBadge } from "@/components/BackendBadge";

interface DashboardSidebarProps {
  activePage: "dashboard" | "datahub" | "crawler" | "voice";
  backendOnline: boolean;
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

const NAV_ITEMS = [
  { id: "dashboard" as const, label: "대시보드", href: "/dashboard", icon: <DashboardIcon /> },
  { id: "datahub" as const, label: "데이터 허브", href: "/datahub", icon: <DatabaseIcon /> },
  { id: "crawler" as const, label: "웹 크롤러", href: "/crawler", icon: <GlobeIcon /> },
  { id: "voice" as const, label: "음성 분석", href: "/voice", icon: <MicrophoneIcon /> },
  { id: "knowledge" as const, label: "지식베이스", href: "/dashboard", icon: <BookIcon /> },
] as const;

export function DashboardSidebar({ activePage, backendOnline, mobileOpen = false, onMobileClose }: DashboardSidebarProps) {
  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:sticky top-0 left-0 z-50 h-screen w-64 bg-white border-r border-gray-200 flex flex-col transition-transform duration-200 ease-in-out
        \${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}>
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
              <LogoIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">SupportAI</span>
          </Link>
          {/* Close button for mobile */}
          <button 
            onClick={onMobileClose} 
            className="lg:hidden p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
          >
            <span className="sr-only">Close sidebar</span>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <nav className="flex-1 p-3 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const isActive = item.id === activePage;
            if (isActive) {
              return (
                <div
                  key={item.id}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-blue-50 text-[#2563EB] mb-1"
                >
                  {item.icon}
                  {item.label}
                </div>
              );
            }
            return (
              <Link
                key={item.id}
                href={item.href}
                onClick={onMobileClose}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-all mb-1"
              >
                {item.icon}
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-200 space-y-3 mt-auto">
          <BackendBadge online={backendOnline} />
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">IB</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">관리자</div>
              <div className="text-xs text-gray-400">Pro 플랜</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
