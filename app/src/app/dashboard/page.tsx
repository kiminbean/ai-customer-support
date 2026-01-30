"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import {
  checkHealth,
  getAnalytics,
  getConversations,
  getDocuments,
  uploadDocument,
  deleteDocument,
  updateSettings as apiUpdateSettings,
  type Analytics,
  type Conversation,
  type Document,
} from "@/lib/api";

// ── Mock data (fallback when backend offline) ──
const MOCK_STATS = [
  { label: "총 대화 수", value: "12,847", change: "+12.5%", icon: "💬" },
  { label: "평균 응답 시간", value: "0.3초", change: "-18.2%", icon: "⚡" },
  { label: "고객 만족도", value: "98.2%", change: "+2.1%", icon: "😊" },
  { label: "활성 채팅", value: "24", change: "+5", icon: "🔥" },
];

const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "1", user: "김서연", avatar: "KS", last_message: "주문한 상품의 배송 상태를 확인하고 싶어요", time: "2분 전", status: "진행중", satisfaction: null },
  { id: "2", user: "이준호", avatar: "LJ", last_message: "반품 절차가 어떻게 되나요?", time: "15분 전", status: "완료", satisfaction: 5 },
  { id: "3", user: "박민지", avatar: "PM", last_message: "쿠폰 코드가 작동하지 않습니다", time: "32분 전", status: "완료", satisfaction: 4 },
  { id: "4", user: "정하늘", avatar: "JH", last_message: "회원가입 시 혜택이 뭔가요?", time: "1시간 전", status: "완료", satisfaction: 5 },
  { id: "5", user: "최우진", avatar: "CW", last_message: "결제 시 오류가 발생합니다", time: "1시간 전", status: "상담원 전환", satisfaction: 3 },
  { id: "6", user: "강예진", avatar: "KY", last_message: "포인트 적립 기준이 궁금합니다", time: "2시간 전", status: "완료", satisfaction: 5 },
  { id: "7", user: "윤도현", avatar: "YD", last_message: "주문 취소는 어떻게 하나요?", time: "3시간 전", status: "완료", satisfaction: 4 },
];

const MOCK_DAILY_CHART = [
  { day: "월", value: 85 }, { day: "화", value: 92 }, { day: "수", value: 78 },
  { day: "목", value: 96 }, { day: "금", value: 88 }, { day: "토", value: 65 }, { day: "일", value: 45 },
];

const MOCK_CATEGORY_DATA = [
  { label: "배송 문의", percentage: 35, color: "#2563EB" },
  { label: "반품/교환", percentage: 25, color: "#7C3AED" },
  { label: "결제 관련", percentage: 20, color: "#F59E0B" },
  { label: "상품 문의", percentage: 12, color: "#10B981" },
  { label: "기타", percentage: 8, color: "#6B7280" },
];

const AI_SETTINGS_DEFAULT = {
  temperature: 0.7,
  maxTokens: 500,
  greeting: "안녕하세요! 👋 무엇을 도와드릴까요?",
  handoffThreshold: 3,
  language: "ko",
  tone: "professional",
};

type TabType = "overview" | "conversations" | "analytics" | "knowledge" | "settings";

// ── Backend Status Badge ──
function BackendBadge({ online }: { online: boolean }) {
  return (
    <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${
      online ? "bg-green-50 text-green-700" : "bg-red-50 text-red-500"
    }`}>
      <span className={`w-2 h-2 rounded-full ${online ? "bg-green-500 animate-pulse" : "bg-red-400"}`} />
      {online ? "백엔드 연결됨" : "오프라인 (데모)"}
    </div>
  );
}

// ── Sidebar ──
function Sidebar({ activeTab, setActiveTab, backendOnline }: { activeTab: TabType; setActiveTab: (t: TabType) => void; backendOnline: boolean }) {
  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    {
      id: "overview", label: "개요",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>,
    },
    {
      id: "conversations", label: "대화 내역",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>,
    },
    {
      id: "analytics", label: "분석",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>,
    },
    {
      id: "knowledge", label: "지식베이스",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>,
    },
    {
      id: "settings", label: "설정",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-100 min-h-screen flex flex-col">
      <div className="p-4 border-b border-gray-100">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#2563EB] rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <span className="text-lg font-bold text-gray-900">SupportAI</span>
        </Link>
      </div>
      <nav className="flex-1 p-3">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all mb-1 ${
              activeTab === tab.id ? "bg-blue-50 text-[#2563EB]" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-100 space-y-3">
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
  );
}

// ── Overview Tab ──
function OverviewTab({ backendOnline, conversations }: { backendOnline: boolean; conversations: Conversation[] }) {
  const stats = MOCK_STATS;
  const displayConversations = conversations.length > 0 ? conversations : MOCK_CONVERSATIONS;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">대시보드</h2>
          <p className="text-sm text-gray-500 mt-1">오늘의 고객지원 현황을 한눈에 확인하세요</p>
        </div>
        <BackendBadge online={backendOnline} />
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white p-5 rounded-xl border border-gray-100">
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
        ))}
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">주간 대화 추이</h3>
          <div className="flex items-end gap-3 h-40">
            {MOCK_DAILY_CHART.map((d) => (
              <div key={d.day} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full flex items-end justify-center" style={{ height: "120px" }}>
                  <div
                    className="w-full max-w-[36px] bg-[#2563EB] rounded-t-md chart-bar hover:bg-[#1d4ed8] transition-colors cursor-pointer"
                    style={{ "--bar-height": `${(d.value / 100) * 120}px`, height: `${(d.value / 100) * 120}px` } as React.CSSProperties}
                    title={`${d.value}건`}
                  />
                </div>
                <span className="text-xs text-gray-400">{d.day}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">문의 카테고리 분포</h3>
          <div className="space-y-3">
            {MOCK_CATEGORY_DATA.map((cat) => (
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
      <div className="bg-white rounded-xl border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">최근 대화</h3>
          <button className="text-xs text-[#2563EB] hover:underline font-medium">전체 보기</button>
        </div>
        <div className="divide-y divide-gray-50">
          {displayConversations.slice(0, 5).map((conv) => (
            <div key={conv.id} className="px-6 py-3.5 flex items-center gap-4 hover:bg-gray-50/50 transition-colors cursor-pointer">
              <div className="w-9 h-9 rounded-full bg-[#2563EB] flex items-center justify-center text-white text-xs font-bold shrink-0">
                {conv.avatar || conv.user?.slice(0, 2) || "?"}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">{conv.user || `대화 #${conv.id}`}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                    conv.status === "진행중" ? "bg-blue-50 text-[#2563EB]"
                      : conv.status === "완료" ? "bg-green-50 text-green-600"
                      : "bg-orange-50 text-orange-600"
                  }`}>{conv.status}</span>
                </div>
                <p className="text-xs text-gray-500 truncate mt-0.5">{conv.last_message}</p>
              </div>
              <div className="text-right shrink-0">
                <div className="text-[10px] text-gray-400">{conv.time}</div>
                {conv.satisfaction && (
                  <div className="flex gap-0.5 mt-1 justify-end">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <span key={i} className={`text-[10px] ${i < conv.satisfaction! ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Conversations Tab ──
function ConversationsTab({ conversations }: { conversations: Conversation[] }) {
  const displayConversations = conversations.length > 0 ? conversations : MOCK_CONVERSATIONS;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">대화 내역</h2>
          <p className="text-sm text-gray-500 mt-1">전체 고객 대화를 관리하세요</p>
        </div>
        <div className="flex gap-2">
          <input type="text" placeholder="검색..." className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30" />
          <select className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 bg-white">
            <option>모든 상태</option>
            <option>진행중</option>
            <option>완료</option>
            <option>상담원 전환</option>
          </select>
        </div>
      </div>
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">고객</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">마지막 메시지</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">상태</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">만족도</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">시간</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {displayConversations.map((conv) => (
              <tr key={conv.id} className="hover:bg-gray-50/50 cursor-pointer transition-colors">
                <td className="px-6 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[#2563EB] flex items-center justify-center text-white text-xs font-bold">
                      {conv.avatar || conv.user?.slice(0, 2) || "?"}
                    </div>
                    <span className="text-sm font-medium text-gray-900">{conv.user || `대화 #${conv.id}`}</span>
                  </div>
                </td>
                <td className="px-6 py-3.5 text-sm text-gray-500 max-w-xs truncate">{conv.last_message}</td>
                <td className="px-6 py-3.5">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    conv.status === "진행중" ? "bg-blue-50 text-[#2563EB]"
                      : conv.status === "완료" ? "bg-green-50 text-green-600"
                      : "bg-orange-50 text-orange-600"
                  }`}>{conv.status}</span>
                </td>
                <td className="px-6 py-3.5">
                  {conv.satisfaction ? (
                    <div className="flex gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <span key={i} className={`text-sm ${i < conv.satisfaction! ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                      ))}
                    </div>
                  ) : <span className="text-xs text-gray-400">—</span>}
                </td>
                <td className="px-6 py-3.5 text-xs text-gray-400">{conv.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Analytics Tab ──
function AnalyticsTab({ analytics }: { analytics: Analytics | null }) {
  const hourlyData = analytics?.hourly_data || [
    { hour: "00", v: 12 }, { hour: "03", v: 5 }, { hour: "06", v: 8 },
    { hour: "09", v: 45 }, { hour: "12", v: 62 }, { hour: "15", v: 58 },
    { hour: "18", v: 42 }, { hour: "21", v: 28 },
  ];
  const maxHourly = Math.max(...hourlyData.map((d) => d.v));

  const satisfactionDist = analytics?.satisfaction_distribution || [
    { stars: 5, count: 847, pct: 66 },
    { stars: 4, count: 265, pct: 21 },
    { stars: 3, count: 102, pct: 8 },
    { stars: 2, count: 41, pct: 3 },
    { stars: 1, count: 25, pct: 2 },
  ];

  const aiResolution = analytics?.ai_resolution_rate ?? 87.3;
  const escalationRate = analytics?.escalation_rate ?? 12.7;
  const avgTurns = analytics?.avg_turns ?? 4.2;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">분석</h2>
        <p className="text-sm text-gray-500 mt-1">고객지원 성과를 분석하고 개선점을 찾으세요</p>
      </div>
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">AI 자동 해결률</div>
          <div className="text-3xl font-bold text-gray-900">{aiResolution}%</div>
          <div className="mt-2 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-green-500 rounded-full" style={{ width: `${aiResolution}%` }} />
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">상담원 전환율</div>
          <div className="text-3xl font-bold text-gray-900">{escalationRate}%</div>
          <div className="mt-2 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-orange-500 rounded-full" style={{ width: `${escalationRate}%` }} />
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">평균 대화 턴수</div>
          <div className="text-3xl font-bold text-gray-900">{avgTurns}회</div>
          <div className="mt-2 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-[#2563EB] rounded-full" style={{ width: `${(avgTurns / 10) * 100}%` }} />
          </div>
        </div>
      </div>
      <div className="bg-white p-6 rounded-xl border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">시간대별 문의량</h3>
        <div className="flex items-end gap-4 h-48">
          {hourlyData.map((d) => (
            <div key={d.hour} className="flex-1 flex flex-col items-center gap-2">
              <span className="text-xs text-gray-500 font-medium">{d.v}</span>
              <div className="w-full flex items-end justify-center" style={{ height: "160px" }}>
                <div
                  className="w-full max-w-[48px] bg-gradient-to-t from-[#2563EB] to-[#3b82f6] rounded-t-md hover:from-[#1d4ed8] hover:to-[#2563EB] transition-colors cursor-pointer"
                  style={{ height: `${(d.v / maxHourly) * 160}px` }}
                  title={`${d.hour}시: ${d.v}건`}
                />
              </div>
              <span className="text-xs text-gray-400">{d.hour}시</span>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-white p-6 rounded-xl border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">만족도 분포</h3>
        <div className="space-y-3">
          {satisfactionDist.map((row) => (
            <div key={row.stars} className="flex items-center gap-3">
              <div className="flex gap-0.5 w-20 shrink-0">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span key={i} className={`text-sm ${i < row.stars ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                ))}
              </div>
              <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-yellow-400 rounded-full transition-all duration-700" style={{ width: `${row.pct}%` }} />
              </div>
              <span className="text-xs text-gray-500 w-16 text-right">{row.count}건 ({row.pct}%)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Knowledge Base Tab ──
function KnowledgeTab({ backendOnline }: { backendOnline: boolean }) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = useCallback(async () => {
    if (!backendOnline) return;
    setLoading(true);
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [backendOnline]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0 || !backendOnline) return;
    setUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        await uploadDocument(files[i]);
      }
      await loadDocuments();
    } catch {
      alert("문서 업로드에 실패했습니다. 백엔드 서버를 확인해주세요.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!backendOnline) return;
    if (!confirm("이 문서를 삭제하시겠습니까?")) return;
    try {
      await deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch {
      alert("문서 삭제에 실패했습니다.");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    handleUpload(e.dataTransfer.files);
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "-";
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">지식베이스</h2>
        <p className="text-sm text-gray-500 mt-1">AI가 참고할 문서를 업로드하고 관리하세요</p>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">등록된 문서</div>
          <div className="text-3xl font-bold text-gray-900">{documents.length}건</div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">마지막 업데이트</div>
          <div className="text-lg font-bold text-gray-900">
            {documents.length > 0
              ? new Date(documents[documents.length - 1].uploaded_at).toLocaleDateString("ko-KR")
              : "-"}
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">백엔드 상태</div>
          <div className={`text-lg font-bold ${backendOnline ? "text-green-600" : "text-red-500"}`}>
            {backendOnline ? "✅ 연결됨" : "❌ 오프라인"}
          </div>
        </div>
      </div>

      {/* Upload area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
          dragActive
            ? "border-[#2563EB] bg-blue-50"
            : backendOnline
            ? "border-gray-200 bg-white hover:border-gray-300"
            : "border-gray-200 bg-gray-50 opacity-60"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md,.docx,.csv"
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
        />
        <div className="text-4xl mb-3">{uploading ? "⏳" : "📁"}</div>
        <h3 className="text-sm font-semibold text-gray-900 mb-1">
          {uploading ? "업로드 중..." : "문서를 드래그하여 업로드하세요"}
        </h3>
        <p className="text-xs text-gray-500 mb-4">
          PDF, TXT, MD, DOCX, CSV 파일을 지원합니다
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={!backendOnline || uploading}
          className="px-4 py-2 bg-[#2563EB] text-white text-sm font-medium rounded-lg hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? "업로드 중..." : "파일 선택"}
        </button>
        {!backendOnline && (
          <p className="text-xs text-red-400 mt-3">⚠️ 백엔드가 오프라인입니다. 문서 업로드를 사용하려면 백엔드를 실행해주세요.</p>
        )}
      </div>

      {/* Document list */}
      <div className="bg-white rounded-xl border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">등록된 문서 ({documents.length})</h3>
        </div>
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">문서 목록을 불러오는 중...</div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">
            {backendOnline ? "등록된 문서가 없습니다. 위에서 문서를 업로드해주세요." : "백엔드가 오프라인이면 문서 목록을 볼 수 없습니다."}
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {documents.map((doc) => (
              <div key={doc.id} className="px-6 py-3.5 flex items-center gap-4 hover:bg-gray-50/50 transition-colors">
                <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-lg shrink-0">📄</div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{doc.filename}</div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {formatFileSize(doc.size)}
                    {doc.chunk_count !== undefined && ` · ${doc.chunk_count}개 청크`}
                    {doc.uploaded_at && ` · ${new Date(doc.uploaded_at).toLocaleString("ko-KR")}`}
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-xs text-red-400 hover:text-red-600 px-3 py-1.5 rounded-lg hover:bg-red-50 transition-colors font-medium"
                >
                  삭제
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Settings Tab ──
function SettingsTab({ backendOnline }: { backendOnline: boolean }) {
  const [settings, setSettings] = useState(AI_SETTINGS_DEFAULT);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (backendOnline) {
        await apiUpdateSettings({
          temperature: settings.temperature,
          max_tokens: settings.maxTokens,
          greeting: settings.greeting,
          handoff_threshold: settings.handoffThreshold,
          language: settings.language,
          tone: settings.tone,
        });
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      alert("설정 저장에 실패했습니다.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">설정</h2>
          <p className="text-sm text-gray-500 mt-1">AI 봇의 동작을 커스터마이즈하세요</p>
        </div>
        <BackendBadge online={backendOnline} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* AI Configuration */}
        <div className="bg-white p-6 rounded-xl border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">AI 모델 설정</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">응답 창의성 (Temperature)</label>
              <input type="range" min="0" max="1" step="0.1" value={settings.temperature}
                onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                className="w-full accent-[#2563EB]" />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>정확한 (0.0)</span>
                <span className="font-medium text-[#2563EB]">{settings.temperature}</span>
                <span>창의적 (1.0)</span>
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">최대 응답 길이 (토큰)</label>
              <input type="number" value={settings.maxTokens}
                onChange={(e) => setSettings({ ...settings, maxTokens: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">응답 톤</label>
              <select value={settings.tone} onChange={(e) => setSettings({ ...settings, tone: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 bg-white">
                <option value="professional">전문적 / 비즈니스</option>
                <option value="friendly">친근한 / 캐주얼</option>
                <option value="formal">격식체 / 공손한</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">상담원 전환 임계값 (실패 횟수)</label>
              <input type="number" value={settings.handoffThreshold}
                onChange={(e) => setSettings({ ...settings, handoffThreshold: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30" />
              <p className="text-[10px] text-gray-400 mt-1">AI가 연속으로 답변에 실패하면 자동으로 상담원에게 전환합니다</p>
            </div>
          </div>
        </div>

        {/* Chat Widget Settings */}
        <div className="bg-white p-6 rounded-xl border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">채팅 위젯 설정</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">환영 메시지</label>
              <textarea value={settings.greeting}
                onChange={(e) => setSettings({ ...settings, greeting: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30 resize-none" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">기본 언어</label>
              <select value={settings.language}
                onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 bg-white">
                <option value="ko">한국어</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
                <option value="zh">中文</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">위젯 위치</label>
              <div className="grid grid-cols-2 gap-2">
                {["우측 하단", "좌측 하단", "우측 상단", "좌측 상단"].map((pos) => (
                  <button key={pos}
                    className="px-3 py-2 text-xs border border-gray-200 rounded-lg hover:border-[#2563EB] hover:text-[#2563EB] transition-colors first:bg-blue-50 first:border-[#2563EB] first:text-[#2563EB]">
                    {pos}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1 block">브랜드 색상</label>
              <div className="flex gap-2">
                {["#2563EB", "#7C3AED", "#059669", "#DC2626", "#F59E0B"].map((color) => (
                  <button key={color}
                    className="w-8 h-8 rounded-full border-2 border-transparent hover:border-gray-300 transition-colors first:ring-2 first:ring-offset-2 first:ring-[#2563EB]"
                    style={{ backgroundColor: color }} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center justify-end gap-3">
        {!backendOnline && (
          <span className="text-xs text-gray-400">⚠️ 오프라인 모드 — 설정이 로컬에만 적용됩니다</span>
        )}
        <button
          onClick={handleSave}
          disabled={saving}
          className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all ${
            saved ? "bg-green-500 text-white"
              : saving ? "bg-gray-300 text-gray-500 cursor-wait"
              : "bg-[#2563EB] text-white hover:bg-[#1d4ed8]"
          }`}
        >
          {saved ? "✓ 저장 완료!" : saving ? "저장 중..." : "설정 저장"}
        </button>
      </div>
    </div>
  );
}

// ── Main Dashboard ──
export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [backendOnline, setBackendOnline] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  // Health check
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    const check = async () => {
      const healthy = await checkHealth();
      setBackendOnline(healthy);
    };
    check();
    interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  // Load data from backend when online
  useEffect(() => {
    if (!backendOnline) return;
    const loadData = async () => {
      try {
        const [convs, stats] = await Promise.all([
          getConversations().catch(() => []),
          getAnalytics().catch(() => null),
        ]);
        setConversations(convs);
        if (stats) setAnalytics(stats);
      } catch {
        // silently fail
      }
    };
    loadData();
  }, [backendOnline]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} backendOnline={backendOnline} />
      <main className="flex-1 p-8 overflow-auto">
        {activeTab === "overview" && <OverviewTab backendOnline={backendOnline} conversations={conversations} />}
        {activeTab === "conversations" && <ConversationsTab conversations={conversations} />}
        {activeTab === "analytics" && <AnalyticsTab analytics={analytics} />}
        {activeTab === "knowledge" && <KnowledgeTab backendOnline={backendOnline} />}
        {activeTab === "settings" && <SettingsTab backendOnline={backendOnline} />}
      </main>
    </div>
  );
}
