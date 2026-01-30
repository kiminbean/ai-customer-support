"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { sendMessage as apiSendMessage, checkHealth, type ChatResponse } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "bot";
  text: string;
  timestamp: Date;
  agentType?: string;
  confidence?: number;
  sources?: { title: string; content?: string; score?: number }[];
}

const FAQ_RESPONSES: Record<string, string> = {
  배송: "📦 일반 배송은 결제 완료 후 2~3일 내에 도착합니다. 제주/도서산간 지역은 1~2일 추가 소요될 수 있습니다.\n\n• 일반배송: 2~3일 (무료)\n• 로켓배송: 당일/익일 (₩3,000)\n• 새벽배송: 주문 다음날 오전 7시 전 도착 (₩4,000)\n\n배송 상태는 [주문 조회] 메뉴에서 실시간으로 확인하실 수 있습니다.",
  반품: "🔄 반품/교환은 상품 수령 후 7일 이내에 가능합니다.\n\n【반품 절차】\n1. 마이페이지 → 주문내역 → 반품신청\n2. 반품 사유 선택\n3. 수거일 지정\n4. 택배 기사 방문 수거\n5. 상품 확인 후 환불 처리 (1~3영업일)\n\n※ 단순 변심의 경우 반품 배송비 ₩3,000이 부과됩니다.",
  결제: "💳 다양한 결제 수단을 지원합니다:\n\n• 신용/체크카드 (모든 카드사)\n• 무통장 입금\n• 카카오페이 / 네이버페이 / 토스\n• 휴대폰 결제\n• 포인트 결제\n\n결제 오류가 발생하시면 카드사 또는 결제 수단의 한도를 확인해주세요. 계속 문제가 있으시면 고객센터(1588-0000)로 연락해주세요.",
  교환: "🔄 교환은 상품 수령 후 7일 이내에 가능합니다.\n\n【교환 절차】\n1. 마이페이지 → 주문내역 → 교환신청\n2. 교환 사유 및 원하시는 옵션 선택\n3. 수거일 지정\n4. 교환 상품 발송 (수거 확인 후 1~2일)\n\n※ 상품 불량의 경우 배송비는 무료입니다.",
  쿠폰: "🎫 쿠폰 사용 방법:\n\n1. 장바구니 또는 결제 페이지에서 '쿠폰 적용' 클릭\n2. 보유 쿠폰 목록에서 선택 또는 쿠폰 코드 직접 입력\n3. '적용' 버튼 클릭\n\n※ 쿠폰은 중복 사용이 불가하며, 최소 주문금액 조건이 있을 수 있습니다.\n\n현재 진행 중인 이벤트:\n• 신규 가입 10% 할인 쿠폰\n• 첫 구매 ₩5,000 할인 쿠폰",
  회원가입: "👤 회원가입은 간단합니다!\n\n1. 홈페이지 우측 상단 '회원가입' 클릭\n2. 이메일 또는 소셜 계정(카카오/네이버/구글)으로 가입\n3. 본인 인증 완료\n4. 가입 완료!\n\n🎁 신규 가입 혜택:\n• 웰컴 쿠폰 ₩5,000\n• 첫 구매 10% 할인\n• 무료 배송 쿠폰 1장",
  포인트: "⭐ 포인트 적립 및 사용 안내:\n\n【적립】\n• 상품 구매 시 결제금액의 1% 적립\n• 리뷰 작성 시 최대 500P 적립\n• 포토리뷰: 500P / 텍스트리뷰: 100P\n\n【사용】\n• 1포인트 = 1원\n• 최소 1,000P 이상부터 사용 가능\n• 결제 시 '포인트 사용'에서 사용\n\n현재 보유 포인트는 마이페이지에서 확인하세요!",
  주문: "📋 주문 조회 방법:\n\n1. 로그인 후 마이페이지 → 주문내역\n2. 주문번호로 검색 (비회원도 가능)\n\n주문 상태:\n• 결제완료 → 상품준비중 → 배송시작 → 배송중 → 배송완료\n\n주문 취소는 '상품준비중' 단계까지만 가능합니다.\n배송 시작 이후에는 반품 절차를 이용해주세요.",
};

function findBestResponse(input: string): string {
  const lower = input.toLowerCase();
  for (const [keyword, response] of Object.entries(FAQ_RESPONSES)) {
    if (lower.includes(keyword)) {
      return response;
    }
  }
  if (lower.match(/안녕|반가|hello|hi |헬로/)) {
    return "안녕하세요! 👋 SupportAI 고객지원 봇입니다. 무엇을 도와드릴까요?\n\n자주 묻는 질문:\n• 배송 조회\n• 반품/교환\n• 결제 문의\n• 쿠폰/포인트\n• 회원가입\n\n위 키워드를 입력하시거나, 궁금하신 내용을 자유롭게 질문해주세요!";
  }
  if (lower.match(/감사|고마|thanks|thank/)) {
    return "감사합니다! 😊 더 궁금하신 사항이 있으시면 언제든 문의해주세요. 항상 최선을 다해 도와드리겠습니다!";
  }
  if (lower.match(/상담[원사]|사람|실제|직접/)) {
    return "🧑‍💼 상담원 연결을 원하시는군요.\n\n현재 상담원 연결 가능 시간:\n• 평일: 09:00 ~ 18:00\n• 토요일: 09:00 ~ 13:00\n• 일요일/공휴일: 휴무\n\n잠시만 기다려주시면 상담원에게 연결해드리겠습니다...\n\n(데모 모드에서는 상담원 연결이 지원되지 않습니다)";
  }
  return "죄송합니다, 해당 질문에 대한 정확한 답변을 찾지 못했습니다. 🤔\n\n다음 주제에 대해 도움을 드릴 수 있습니다:\n• 배송 조회 및 배송 관련 문의\n• 반품/교환 절차\n• 결제 수단 및 결제 오류\n• 쿠폰 사용 방법\n• 회원가입 및 혜택\n• 포인트 적립/사용\n• 주문 조회/취소\n\n위 키워드를 포함하여 다시 질문해주시거나, '상담원 연결'을 입력하시면 전문 상담원에게 연결해드립니다.";
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
}

function getAgentBadge(agentType?: string) {
  switch (agentType) {
    case "faq":
      return { label: "🔍 FAQ 에이전트", color: "bg-blue-50 text-blue-700 border-blue-200" };
    case "order":
      return { label: "📦 주문조회 에이전트", color: "bg-green-50 text-green-700 border-green-200" };
    case "escalation":
      return { label: "👤 상담원 연결", color: "bg-orange-50 text-orange-700 border-orange-200" };
    default:
      return null;
  }
}

function getConfidenceInfo(confidence?: number) {
  if (confidence === undefined || confidence === null) return null;
  if (confidence >= 0.8) return { label: "높음", color: "bg-green-500", textColor: "text-green-700", bgColor: "bg-green-100" };
  if (confidence >= 0.5) return { label: "중간", color: "bg-yellow-500", textColor: "text-yellow-700", bgColor: "bg-yellow-100" };
  return { label: "낮음", color: "bg-red-500", textColor: "text-red-700", bgColor: "bg-red-100" };
}

function SourceDocuments({ sources }: { sources: { title: string; content?: string; score?: number }[] }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-[11px] text-blue-600 hover:text-blue-800 transition-colors font-medium"
      >
        <svg
          className={`w-3 h-3 transition-transform ${expanded ? "rotate-90" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        📄 참고 문서 ({sources.length})
      </button>
      {expanded && (
        <div className="mt-1.5 space-y-1.5 animate-fade-in-up">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="px-3 py-2 bg-blue-50/50 rounded-lg border border-blue-100 text-[11px]"
            >
              <div className="font-medium text-blue-800">{src.title}</div>
              {src.content && (
                <div className="text-blue-600 mt-0.5 line-clamp-2">{src.content}</div>
              )}
              {src.score !== undefined && (
                <div className="text-blue-400 mt-0.5">관련도: {Math.round(src.score * 100)}%</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DemoPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "bot",
      text: "안녕하세요! 👋 SupportAI 고객지원 봇입니다.\n무엇을 도와드릴까요?\n\n자주 묻는 질문:\n• 배송 조회\n• 반품/교환\n• 결제 문의\n• 쿠폰/포인트",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, scrollToBottom]);

  // Check backend health on mount and periodically
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

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      text: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = input.trim();
    setInput("");
    setIsTyping(true);

    let botMessage: Message;

    if (backendOnline) {
      try {
        const data: ChatResponse = await apiSendMessage(messageText, conversationId);
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }
        botMessage = {
          id: (Date.now() + 1).toString(),
          role: "bot",
          text: data.response,
          timestamp: new Date(),
          agentType: data.agent_type,
          confidence: data.confidence,
          sources: data.sources,
        };
      } catch {
        // Fallback to local mock
        await new Promise((resolve) => setTimeout(resolve, 400));
        const responseText = findBestResponse(messageText);
        botMessage = {
          id: (Date.now() + 1).toString(),
          role: "bot",
          text: responseText,
          timestamp: new Date(),
        };
      }
    } else {
      // Local mock mode
      await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 1200));
      const responseText = findBestResponse(messageText);
      botMessage = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        text: responseText,
        timestamp: new Date(),
      };
    }

    setIsTyping(false);
    setMessages((prev) => [...prev, botMessage]);
    inputRef.current?.focus();
  };

  const quickQuestions = ["배송 조회", "반품 신청", "결제 오류", "쿠폰 사용법"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 bg-[#2563EB] rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <span className="text-lg font-bold text-gray-900">SupportAI</span>
            </Link>
            <div className="flex items-center gap-3">
              {/* Backend status indicator */}
              <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${
                backendOnline
                  ? "bg-green-50 text-green-700"
                  : "bg-gray-100 text-gray-400"
              }`}>
                <span className={`w-2 h-2 rounded-full ${backendOnline ? "bg-green-500 animate-pulse" : "bg-gray-400"}`} />
                {backendOnline ? "AI 백엔드 연결됨" : "데모 모드"}
              </span>
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← 홈으로</Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">AI 채팅 데모</h1>
          <p className="text-sm text-gray-500 mt-1">
            {backendOnline
              ? "🟢 AI 백엔드에 연결되었습니다 — 실시간 RAG 기반 응답"
              : "실시간 AI 고객지원 체험 — 이커머스 시나리오"}
          </p>
        </div>

        {/* Chat container */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 overflow-hidden">
          {/* Chat header */}
          <div className="bg-[#2563EB] px-6 py-4 flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm">SupportAI 봇</h3>
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${backendOnline ? "bg-green-400" : "bg-yellow-400"}`} />
                <span className="text-blue-100 text-xs">
                  {backendOnline ? "온라인 · AI 백엔드 연결됨" : "온라인 · 로컬 데모 모드"}
                </span>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="h-[480px] overflow-y-auto p-6 space-y-4 bg-gray-50/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-end gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in-up`}
              >
                {msg.role === "bot" && (
                  <div className="w-8 h-8 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0 mb-5">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
                <div className={`max-w-[75%] ${msg.role === "user" ? "order-1" : ""}`}>
                  <div
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                      msg.role === "user"
                        ? "bg-[#2563EB] text-white rounded-br-md"
                        : "bg-white text-gray-700 rounded-bl-md shadow-sm border border-gray-100"
                    }`}
                  >
                    {msg.text}
                  </div>
                  {/* Agent badge + confidence for bot messages */}
                  {msg.role === "bot" && (msg.agentType || msg.confidence !== undefined) && (
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      {(() => {
                        const badge = getAgentBadge(msg.agentType);
                        return badge ? (
                          <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${badge.color}`}>
                            {badge.label}
                          </span>
                        ) : null;
                      })()}
                      {(() => {
                        const conf = getConfidenceInfo(msg.confidence);
                        return conf ? (
                          <span className={`flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-medium ${conf.bgColor} ${conf.textColor}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${conf.color}`} />
                            신뢰도: {conf.label} ({Math.round((msg.confidence ?? 0) * 100)}%)
                          </span>
                        ) : null;
                      })()}
                    </div>
                  )}
                  {/* Source documents */}
                  {msg.role === "bot" && msg.sources && msg.sources.length > 0 && (
                    <SourceDocuments sources={msg.sources} />
                  )}
                  <span className={`text-[10px] text-gray-400 mt-1 block ${msg.role === "user" ? "text-right" : "text-left"}`}>
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex items-end gap-2 animate-fade-in-up">
                <div className="w-8 h-8 rounded-full bg-[#2563EB] flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-md shadow-sm border border-gray-100">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick questions */}
          <div className="px-4 py-2 border-t border-gray-100 bg-white">
            <div className="flex gap-2 overflow-x-auto pb-1">
              {quickQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setInput(q);
                    setTimeout(() => {
                      const fakeEvent = { preventDefault: () => {} };
                      void fakeEvent;
                    }, 0);
                  }}
                  className="shrink-0 px-3 py-1.5 text-xs bg-blue-50 text-[#2563EB] rounded-full hover:bg-blue-100 transition-colors font-medium"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="px-4 pb-4 pt-2 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex gap-2"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="메시지를 입력하세요..."
                className="flex-1 px-4 py-3 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:bg-white border border-transparent focus:border-[#2563EB]/30 transition-all"
              />
              <button
                type="submit"
                disabled={!input.trim()}
                className="px-4 py-3 bg-[#2563EB] text-white rounded-xl hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>
        </div>

        {/* Info cards */}
        <div className="mt-8 grid sm:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-100">
            <div className="text-2xl mb-2">⚡</div>
            <h3 className="font-semibold text-sm text-gray-900">즉각 응답</h3>
            <p className="text-xs text-gray-500 mt-1">평균 0.3초 내 AI 자동 응답</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-100">
            <div className="text-2xl mb-2">🧠</div>
            <h3 className="font-semibold text-sm text-gray-900">컨텍스트 이해</h3>
            <p className="text-xs text-gray-500 mt-1">대화 맥락을 파악하여 정확한 답변</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-100">
            <div className="text-2xl mb-2">🔄</div>
            <h3 className="font-semibold text-sm text-gray-900">상담원 연결</h3>
            <p className="text-xs text-gray-500 mt-1">필요 시 실제 상담원에게 자동 전환</p>
          </div>
        </div>
      </div>
    </div>
  );
}
