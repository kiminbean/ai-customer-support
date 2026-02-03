/**
 * Shared mock data constants
 * Consolidated from inline definitions across components
 */

import type { Analytics, Conversation } from "./api";

// ── Stats ──
export const MOCK_STATS = [
  { label: "총 대화 수", value: "12,847", change: "+12.5%", icon: "💬" },
  { label: "평균 응답 시간", value: "0.3초", change: "-18.2%", icon: "⚡" },
  { label: "고객 만족도", value: "98.2%", change: "+2.1%", icon: "😊" },
  { label: "활성 채팅", value: "24", change: "+5", icon: "🔥" },
] as const;

export const MOCK_STATS_EN = [
  { label: "Total conversations", value: "12,847", change: "+12.5%", icon: "💬" },
  { label: "Avg response time", value: "0.3s", change: "-18.2%", icon: "⚡" },
  { label: "Customer satisfaction", value: "98.2%", change: "+2.1%", icon: "😊" },
  { label: "Active chats", value: "24", change: "+5", icon: "🔥" },
] as const;

// ── Conversations ──
export const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "1", user: "김서연", avatar: "KS", last_message: "주문한 상품의 배송 상태를 확인하고 싶어요", time: "2분 전", status: "진행중", satisfaction: null },
  { id: "2", user: "이준호", avatar: "LJ", last_message: "반품 절차가 어떻게 되나요?", time: "15분 전", status: "완료", satisfaction: 5 },
  { id: "3", user: "박민지", avatar: "PM", last_message: "쿠폰 코드가 작동하지 않습니다", time: "32분 전", status: "완료", satisfaction: 4 },
  { id: "4", user: "정하늘", avatar: "JH", last_message: "회원가입 시 혜택이 뭔가요?", time: "1시간 전", status: "완료", satisfaction: 5 },
  { id: "5", user: "최우진", avatar: "CW", last_message: "결제 시 오류가 발생합니다", time: "1시간 전", status: "상담원 전환", satisfaction: 3 },
  { id: "6", user: "강예진", avatar: "KY", last_message: "포인트 적립 기준이 궁금합니다", time: "2시간 전", status: "완료", satisfaction: 5 },
  { id: "7", user: "윤도현", avatar: "YD", last_message: "주문 취소는 어떻게 하나요?", time: "3시간 전", status: "완료", satisfaction: 4 },
];

// ── Daily Chart ──
export const MOCK_DAILY_CHART = [
  { day: "월", value: 85 }, { day: "화", value: 92 }, { day: "수", value: 78 },
  { day: "목", value: 96 }, { day: "금", value: 88 }, { day: "토", value: 65 }, { day: "일", value: 45 },
] as const;

export const MOCK_DAILY_CHART_EN = [
  { day: "Mon", value: 85 }, { day: "Tue", value: 92 }, { day: "Wed", value: 78 },
  { day: "Thu", value: 96 }, { day: "Fri", value: 88 }, { day: "Sat", value: 65 }, { day: "Sun", value: 45 },
] as const;

// ── Category Data ──
export const MOCK_CATEGORY_DATA = [
  { label: "배송 문의", percentage: 35, color: "#2563EB" },
  { label: "반품/교환", percentage: 25, color: "#7C3AED" },
  { label: "결제 관련", percentage: 20, color: "#F59E0B" },
  { label: "상품 문의", percentage: 12, color: "#10B981" },
  { label: "기타", percentage: 8, color: "#6B7280" },
] as const;

export const MOCK_CATEGORY_DATA_EN = [
  { label: "Shipping issues", percentage: 35, color: "#2563EB" },
  { label: "Returns/Exchanges", percentage: 25, color: "#7C3AED" },
  { label: "Payment issues", percentage: 20, color: "#F59E0B" },
  { label: "Product inquiries", percentage: 12, color: "#10B981" },
  { label: "Other", percentage: 8, color: "#6B7280" },
] as const;

// ── Satisfaction Distribution ──
export const MOCK_SATISFACTION_DIST = [
  { stars: 5, count: 847, pct: 66 },
  { stars: 4, count: 265, pct: 21 },
  { stars: 3, count: 102, pct: 8 },
  { stars: 2, count: 41, pct: 3 },
  { stars: 1, count: 25, pct: 2 },
] as const;

// ── Hourly Data ──
export const MOCK_HOURLY_DATA = [
  { hour: "00", v: 12 }, { hour: "03", v: 5 }, { hour: "06", v: 8 },
  { hour: "09", v: 45 }, { hour: "12", v: 62 }, { hour: "15", v: 58 },
  { hour: "18", v: 42 }, { hour: "21", v: 28 },
] as const;

// ── Status Colors ──
export const STATUS_COLORS = {
  "진행중": "bg-blue-50 text-[#2563EB]",
  "완료": "bg-green-50 text-green-600",
  "상담원 전환": "bg-orange-50 text-orange-600",
  "In Progress": "bg-blue-50 text-[#2563EB]",
  "Completed": "bg-green-50 text-green-600",
  "Escalated": "bg-orange-50 text-orange-600",
} as const;

// ── AI Settings Default ──
export const AI_SETTINGS_DEFAULT = {
  temperature: 0.7,
  maxTokens: 500,
  greeting: "안녕하세요! 👋 무엇을 도와드릴까요?",
  handoffThreshold: 3,
  language: "ko",
  tone: "professional",
} as const;
