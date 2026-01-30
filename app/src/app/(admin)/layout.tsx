"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { DashboardSidebar } from "@/components/DashboardSidebar";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import { LogoIcon } from "@/components/icons";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const backendOnline = useHealthCheck();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Detect active page from pathname
  const activePage = pathname.startsWith("/voice") ? "voice"
    : pathname.startsWith("/crawler") ? "crawler"
    : pathname.startsWith("/datahub") ? "datahub"
    : "dashboard";
  
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Mobile Top Bar */}
      <div className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-30 flex items-center justify-between px-4 lg:hidden">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
            <LogoIcon className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-gray-900">SupportAI</span>
        </div>
        <button 
          onClick={() => setSidebarOpen(true)}
          className="p-2 -mr-2 text-gray-600 hover:text-gray-900"
        >
          <span className="sr-only">Open sidebar</span>
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
      </div>

      <DashboardSidebar 
        activePage={activePage} 
        backendOnline={backendOnline} 
        mobileOpen={sidebarOpen}
        onMobileClose={() => setSidebarOpen(false)}
      />
      <main className="flex-1 overflow-auto pt-16 lg:pt-0">
        {children}
      </main>
    </div>
  );
}
