"use client";

import { usePathname } from "next/navigation";
import { DashboardSidebar } from "@/components/DashboardSidebar";
import { useHealthCheck } from "@/hooks/useHealthCheck";

type ActivePage = "dashboard" | "datahub" | "crawler" | "voice";

function getActivePage(pathname: string): ActivePage {
  if (pathname.includes("/datahub")) return "datahub";
  if (pathname.includes("/crawler")) return "crawler";
  if (pathname.includes("/voice")) return "voice";
  return "dashboard";
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const backendOnline = useHealthCheck();
  const activePage = getActivePage(pathname);

  return (
    <div className="min-h-screen bg-gray-50/50">
      <DashboardSidebar activePage={activePage} backendOnline={backendOnline} />
      <div className="lg:pl-64">
        <main className="min-h-screen">{children}</main>
      </div>
    </div>
  );
}
