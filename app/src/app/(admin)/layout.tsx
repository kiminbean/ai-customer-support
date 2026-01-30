"use client";

import { usePathname } from "next/navigation";
import { DashboardSidebar } from "@/components/DashboardSidebar";
import { useHealthCheck } from "@/hooks/useHealthCheck";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const backendOnline = useHealthCheck();
  
  // Detect active page from pathname
  const activePage = pathname.startsWith("/voice") ? "voice"
    : pathname.startsWith("/crawler") ? "crawler"
    : pathname.startsWith("/datahub") ? "datahub"
    : "dashboard";
  
  return (
    <div className="flex min-h-screen bg-gray-50">
      <DashboardSidebar activePage={activePage} backendOnline={backendOnline} />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
