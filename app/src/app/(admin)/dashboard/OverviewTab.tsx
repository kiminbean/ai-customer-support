"use client";

import type { Analytics, Conversation, Document } from "@/lib/api";
import { BackendBadge } from "@/components/BackendBadge";

interface OverviewTabProps {
  backendOnline: boolean;
  conversations: Conversation[];
  analytics: Analytics | null;
  documents: Document[];
  isLoading: boolean;
  isDemo: boolean;
}

const MOCK_STATS = [
  { label: "Total conversations", value: "12,847", change: "+12.5%", icon: "💬" },
  { label: "Avg response time", value: "0.3s", change: "-18.2%", icon: "⚡" },
  { label: "Customer satisfaction", value: "98.2%", change: "+2.1%", icon: "😊" },
  { label: "Active chats", value: "24", change: "+5", icon: "🔥" },
];

const MOCK_DAILY_CHART = [
  { day: "Mon", value: 85 }, { day: "Tue", value: 92 }, { day: "Wed", value: 78 },
  { day: "Thu", value: 96 }, { day: "Fri", value: 88 }, { day: "Sat", value: 65 }, { day: "Sun", value: 45 },
];

const MOCK_CATEGORY_DATA = [
  { label: "Shipping issues", percentage: 35, color: "#2563EB" },
  { label: "Returns/Exchanges", percentage: 25, color: "#7C3AED" },
  { label: "Payment issues", percentage: 20, color: "#F59E0B" },
  { label: "Product inquiries", percentage: 12, color: "#10B981" },
  { label: "Other", percentage: 8, color: "#6B7280" },
];

const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "1", user: "김서연", avatar: "KS", last_message: "주문한 상품의 배송 상태를 확인하고 싶어요", time: "2분 전", status: "진행중", satisfaction: null },
  { id: "2", user: "이준호", avatar: "LJ", last_message: "반품 절차가 어떻게 되나요?", time: "15분 전", status: "완료", satisfaction: 5 },
  { id: "3", user: "박민지", avatar: "PM", last_message: "쿠폰 코드가 작동하지 않습니다", time: "32분 전", status: "완료", satisfaction: 4 },
  { id: "4", user: "정하늘", avatar: "JH", last_message: "회원가입 시 혜택이 뭔가요?", time: "1시간 전", status: "완료", satisfaction: 5 },
  { id: "5", user: "최우진", avatar: "CW", last_message: "결제 시 오류가 발생합니다", time: "1시간 전", status: "상담원 전환", satisfaction: 3 },
];

function OverviewTab({ backendOnline, conversations, analytics, documents, isLoading, isDemo }: OverviewTabProps) {
  const stats = analytics ? [
    { label: "Total conversations", value: analytics.total_conversations.toLocaleString(), change: "+12.5%", icon: "💬" },
    { label: "Avg response time", value: analytics.avg_response_time, change: "-18.2%", icon: "⚡" },
    { label: "Customer satisfaction", value: analytics.satisfaction_rate, change: "+2.1%", icon: "😊" },
    { label: "Active chats", value: String(analytics.active_chats), change: "+5", icon: "🔥" },
  ] : MOCK_STATS;

  const displayConversations = conversations.length > 0 ? conversations : MOCK_CONVERSATIONS;
  const dailyChart = analytics?.daily_data || MOCK_DAILY_CHART;
  const categoryData = analytics?.category_data || MOCK_CATEGORY_DATA;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            View today customer support status at a glance
            {documents.length > 0 && <span> · {documents.length} documents</span>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isDemo && (
            <span className="px-2.5 py-1 text-xs font-medium bg-amber-50 text-amber-600 border border-amber-200 rounded-full">
              Demo data
            </span>
          )}
          <BackendBadge online={backendOnline} />
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm animate-pulse">
              <div className="flex items-center justify-between">
                <div className="w-8 h-8 bg-gray-200 rounded" />
                <div className="w-12 h-5 bg-gray-200 rounded-full" />
              </div>
              <div className="mt-3">
                <div className="w-20 h-7 bg-gray-200 rounded" />
                <div className="w-16 h-3 bg-gray-100 rounded mt-2" />
              </div>
            </div>
          ))
        ) : (
          stats.map((stat) => (
            <div key={stat.label} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-2xl">{stat.icon}</span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  stat.change.startsWith("+") ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"
                }`}>{stat.change}</span>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-500 mt-0.5">{stat.label}</div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Weekly conversation trends</h3>
          <div className="flex items-end gap-3 h-40">
            {dailyChart.map((d) => (
              <div key={d.day} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex items-end justify-center" style={{ height: "120px" }}>
                  <div
                    className="w-full max-w-[36px] bg-[#2563EB] rounded-t-md hover:bg-[#1d4ed8] transition-colors cursor-pointer"
                    style={{ height: `${(d.value / 100) * 120}px` }}
                    title={`${d.value} items`}
                  />
                </div>
                <span className="text-xs text-gray-400">{d.day}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Inquiry category distribution</h3>
          <div className="space-y-3">
            {categoryData.map((cat) => (
              <div key={cat.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{cat.label}</span>
                  <span className="font-medium text-gray-900">{cat.percentage}%</span>
                </div>
                <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-1000" style={{ width: `${cat.percentage}%`, backgroundColor: cat.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent conversations */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Recent conversations</h3>
          <button className="text-xs text-[#2563EB] hover:underline font-medium">View all</button>
        </div>
        <div className="divide-y divide-gray-50">
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="px-6 py-3.5 flex items-center gap-4 animate-pulse">
                <div className="w-9 h-9 rounded-full bg-gray-200 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="w-24 h-4 bg-gray-200 rounded mb-2" />
                  <div className="w-40 h-3 bg-gray-100 rounded" />
                </div>
                <div className="w-12 h-3 bg-gray-100 rounded" />
              </div>
            ))
          ) : (
            displayConversations.slice(0, 5).map((conv) => (
              <div key={conv.id} className="px-6 py-3.5 flex items-center gap-4 hover:bg-gray-50/50 transition-colors cursor-pointer">
                <div className="w-9 h-9 rounded-full bg-[#2563EB] flex items-center justify-center text-white text-xs font-bold shrink-0">
                  {conv.avatar || conv.user?.slice(0, 2) || "?"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900">{conv.user || `Conversation #${conv.id}`}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                      conv.status === "진행중" ? "bg-blue-50 text-[#2563EB]"
                      : conv.status === "완료" ? "bg-green-50 text-green-600"
                      : "bg-orange-50 text-orange-600"
                    }`}>{conv.status}</span>
                  </div>
                  <p className="text-xs text-gray-500 truncate mt-0.5">{conv.last_message}</p>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-[10px] text-gray-400">{conv.time}</div>
                  {conv.satisfaction != null && (
                    <div className="flex gap-0.5 mt-1 justify-end">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <span key={i} className={`text-[10px] ${i < conv.satisfaction! ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default OverviewTab;
