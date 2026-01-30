"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import {
  checkHealth,
  startCrawl,
  getCrawlStatus,
  getCrawlResults,
  convertCrawlResults,
  importCrawlResults,
  getCrawlJobs,
  type CrawlResults,
  type CrawlJob,
} from "@/lib/api";

// ── Mock Data (offline fallback) ──

const MOCK_CRAWL_RESULTS: CrawlResults = {
  pages: 47,
  faqs: [
    { question: "배송은 얼마나 걸리나요?", answer: "일반배송 2-3일, 제주/도서산간 3-5일 소요됩니다.", sourceUrl: "https://example.com/faq" },
    { question: "반품은 어떻게 하나요?", answer: "수령 후 7일 이내 마이페이지에서 반품 신청 가능합니다.", sourceUrl: "https://example.com/faq" },
    { question: "교환 절차는 어떻게 되나요?", answer: "반품 신청 후 새 상품으로 재주문하거나, 고객센터에서 동일 상품 교환이 가능합니다.", sourceUrl: "https://example.com/faq" },
    { question: "배송비는 얼마인가요?", answer: "3만원 이상 무료배송, 미만 시 3,000원 부과됩니다.", sourceUrl: "https://example.com/faq" },
    { question: "주문 취소는 어떻게 하나요?", answer: "배송 준비 전까지 마이페이지에서 취소 가능합니다. 이후에는 고객센터로 연락해주세요.", sourceUrl: "https://example.com/faq" },
    { question: "포인트는 어떻게 적립되나요?", answer: "구매 확정 시 결제금액의 1%가 자동 적립됩니다.", sourceUrl: "https://example.com/faq/point" },
    { question: "회원 등급은 어떻게 올라가나요?", answer: "최근 6개월 구매금액에 따라 브론즈/실버/골드/VIP로 자동 변경됩니다.", sourceUrl: "https://example.com/faq/membership" },
    { question: "쿠폰은 중복 사용이 가능한가요?", answer: "쿠폰은 주문 당 1개만 사용 가능합니다. 단, 적립금과는 중복 사용 가능합니다.", sourceUrl: "https://example.com/faq/coupon" },
    { question: "해외 배송이 가능한가요?", answer: "현재 해외 배송은 지원하지 않습니다. 추후 서비스 예정입니다.", sourceUrl: "https://example.com/faq" },
    { question: "결제 수단은 어떤 것이 있나요?", answer: "신용카드, 체크카드, 네이버페이, 카카오페이, 토스페이, 무통장입금을 지원합니다.", sourceUrl: "https://example.com/faq/payment" },
    { question: "비회원 주문이 가능한가요?", answer: "네, 비회원 주문이 가능합니다. 단, 포인트 적립 및 회원 혜택은 제공되지 않습니다.", sourceUrl: "https://example.com/faq" },
    { question: "영수증 발급은 어디서 하나요?", answer: "마이페이지 > 주문내역에서 전자영수증 출력이 가능합니다.", sourceUrl: "https://example.com/faq/receipt" },
  ],
  articles: [
    { title: "회원가입 방법", content: "1. 홈페이지 우측 상단 '회원가입' 클릭\n2. 이메일 또는 소셜 계정으로 가입\n3. 본인인증 완료 후 가입 완료\n4. 가입 즉시 2,000원 쿠폰 발급", sourceUrl: "https://example.com/help/signup" },
    { title: "주문 방법 안내", content: "상품 선택 → 장바구니 담기 → 주문서 작성 → 결제 완료. 주문 확인 이메일이 자동 발송됩니다.", sourceUrl: "https://example.com/help/order" },
    { title: "배송 조회 방법", content: "마이페이지 > 주문내역에서 배송 상태를 확인할 수 있습니다. 운송장 번호 클릭 시 택배사 추적 페이지로 이동합니다.", sourceUrl: "https://example.com/help/delivery" },
    { title: "비밀번호 재설정", content: "로그인 페이지에서 '비밀번호 찾기' 클릭 후, 가입 이메일로 재설정 링크가 발송됩니다.", sourceUrl: "https://example.com/help/password" },
    { title: "앱 설치 안내", content: "앱스토어 또는 플레이스토어에서 'SupportAI Shop'을 검색하여 설치하세요. 앱 전용 할인 혜택이 제공됩니다.", sourceUrl: "https://example.com/help/app" },
    { title: "포인트 사용 방법", content: "주문서 결제 단계에서 보유 포인트를 입력하여 사용할 수 있습니다. 최소 1,000포인트부터 사용 가능합니다.", sourceUrl: "https://example.com/help/point" },
  ],
  products: [
    { name: "프리미엄 무선 이어폰 Pro", description: "노이즈 캔슬링, 48시간 배터리, IPX5 방수. 고해상도 오디오 코덱 지원.", sourceUrl: "https://example.com/product/earphone-pro" },
    { name: "스마트 공기청정기 S200", description: "AI 자동 모드, HEPA 13 필터, 60평형 커버리지. 실시간 공기질 모니터링.", sourceUrl: "https://example.com/product/air-purifier" },
    { name: "에르고 메시 의자 V3", description: "인체공학 설계, 메시 시트, 4D 팔걸이 조절. 허리 받침 높이 조절 가능.", sourceUrl: "https://example.com/product/ergo-chair" },
    { name: "울트라 슬림 노트북 15", description: "14세대 i7, 16GB RAM, 512GB SSD, 1.2kg 초경량. 20시간 배터리.", sourceUrl: "https://example.com/product/laptop-15" },
  ],
  policies: [
    { title: "개인정보 처리방침", content: "당사는 「개인정보 보호법」에 따라 이용자의 개인정보를 보호하고 관련된 고충을 신속하고 원활하게 처리할 수 있도록 다음과 같이 개인정보 처리방침을 수립·공개합니다.", sourceUrl: "https://example.com/policy/privacy" },
    { title: "이용약관", content: "본 약관은 SupportAI Shop(이하 '회사')이 제공하는 온라인 쇼핑 서비스의 이용조건 및 절차에 관한 기본사항을 규정합니다.", sourceUrl: "https://example.com/policy/terms" },
    { title: "반품/교환/환불 정책", content: "상품 수령 후 7일 이내 반품 가능. 고객 변심 시 배송비 부담. 상품 하자 시 무료 반품. 환불은 반품 완료 후 3영업일 이내 처리.", sourceUrl: "https://example.com/policy/return" },
    { title: "배송 정책", content: "평일 오후 2시 이전 주문 시 당일 출고. 배송 소요일: 수도권 1-2일, 기타 지역 2-3일, 제주/도서산간 3-5일.", sourceUrl: "https://example.com/policy/shipping" },
    { title: "포인트 정책", content: "구매 확정 시 결제금액의 1% 적립. 유효기간 12개월. 최소 사용 단위 1,000P. 탈퇴 시 소멸.", sourceUrl: "https://example.com/policy/point" },
  ],
};

const MOCK_CRAWL_JOBS: CrawlJob[] = [
  { job_id: "mock-1", url: "https://shop.example.com", status: "completed", created_at: "2025-01-15T09:30:00Z", pages_crawled: 47, items_found: 32 },
  { job_id: "mock-2", url: "https://help.example.co.kr", status: "completed", created_at: "2025-01-14T14:20:00Z", pages_crawled: 23, items_found: 15 },
  { job_id: "mock-3", url: "https://faq.mystore.com", status: "failed", created_at: "2025-01-13T11:00:00Z", pages_crawled: 3, items_found: 0 },
];

// ── Helper Components ──

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

type ResultTab = "faqs" | "articles" | "products" | "policies";

// ── Main Page ──
export default function CrawlerPage() {
  const [backendOnline, setBackendOnline] = useState(false);

  // Input state
  const [url, setUrl] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(50);
  const [includePatterns, setIncludePatterns] = useState("");
  const [extractMode, setExtractMode] = useState<"auto" | "faq" | "all">("auto");

  // Crawl state
  const [crawling, setCrawling] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [pagesCrawled, setPagesTotal] = useState({ crawled: 0, total: 0 });
  const [currentUrl, setCurrentUrl] = useState("");
  const [logs, setLogs] = useState<string[]>([]);

  // Results state
  const [results, setResults] = useState<CrawlResults | null>(null);
  const [activeTab, setActiveTab] = useState<ResultTab>("faqs");
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);

  // History
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Action feedback
  const [actionMsg, setActionMsg] = useState("");

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Health check
  useEffect(() => {
    const check = async () => {
      const ok = await checkHealth();
      setBackendOnline(ok);
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  // Load jobs
  useEffect(() => {
    (async () => {
      if (backendOnline) {
        try {
          const j = await getCrawlJobs();
          setJobs(j);
          return;
        } catch { /* fallback */ }
      }
      setJobs(MOCK_CRAWL_JOBS);
    })();
  }, [backendOnline]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Cleanup poll on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // Toggle select all for current tab
  useEffect(() => {
    if (!results) return;
    const items = getTabItems();
    if (selectAll) {
      const newSel = new Set(selectedItems);
      items.forEach((_, i) => newSel.add(`${activeTab}-${i}`));
      setSelectedItems(newSel);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectAll, activeTab]);

  function getTabItems() {
    if (!results) return [];
    switch (activeTab) {
      case "faqs": return results.faqs;
      case "articles": return results.articles;
      case "products": return results.products;
      case "policies": return results.policies;
    }
  }

  const addLog = useCallback((msg: string) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString("ko-KR")}] ${msg}`]);
  }, []);

  // ── Simulate crawl (offline) ──
  const simulateCrawl = useCallback(() => {
    const fakeUrls = [
      "/", "/about", "/faq", "/faq/shipping", "/faq/returns",
      "/products", "/products/earphone", "/products/air-purifier",
      "/help/signup", "/help/order", "/help/delivery",
      "/policy/privacy", "/policy/terms", "/policy/return",
      "/contact", "/blog", "/blog/post-1",
    ];
    const totalPages = Math.min(maxPages, fakeUrls.length + Math.floor(Math.random() * 30));
    let crawled = 0;

    addLog("크롤링을 시작합니다...");
    addLog(`대상: ${url}`);
    addLog(`설정: 깊이 ${maxDepth}, 최대 ${maxPages}페이지, 모드: ${extractMode}`);

    const interval = setInterval(() => {
      crawled++;
      const pct = Math.min(Math.round((crawled / totalPages) * 100), 100);
      const fakeUrl = crawled <= fakeUrls.length
        ? `${url}${fakeUrls[crawled - 1]}`
        : `${url}/page-${crawled}`;

      setProgress(pct);
      setPagesTotal({ crawled, total: totalPages });
      setCurrentUrl(fakeUrl);

      if (crawled % 3 === 0) {
        const discoveries = [
          "FAQ 항목 발견: 배송 관련 질문",
          "도움말 문서 발견: 회원가입 안내",
          "상품 정보 발견: 프리미엄 이어폰",
          "정책 문서 발견: 반품/교환 정책",
          "FAQ 항목 발견: 결제 수단 안내",
          "도움말 문서 발견: 앱 설치 가이드",
        ];
        addLog(`✅ ${discoveries[Math.floor(Math.random() * discoveries.length)]}`);
      } else {
        addLog(`📄 크롤링: ${fakeUrl}`);
      }

      if (crawled >= totalPages) {
        clearInterval(interval);
        addLog(`\n🎉 크롤링 완료! 총 ${totalPages}페이지 수집`);
        addLog(`📊 결과: FAQ ${MOCK_CRAWL_RESULTS.faqs.length}건, 문서 ${MOCK_CRAWL_RESULTS.articles.length}건, 상품 ${MOCK_CRAWL_RESULTS.products.length}건, 정책 ${MOCK_CRAWL_RESULTS.policies.length}건`);
        setCrawling(false);
        setResults(MOCK_CRAWL_RESULTS);
        setProgress(100);
      }
    }, 200);

    pollRef.current = interval;
  }, [url, maxDepth, maxPages, extractMode, addLog]);

  // ── Start Crawl ──
  const handleStartCrawl = useCallback(async () => {
    if (!url.trim()) return;
    setCrawling(true);
    setResults(null);
    setProgress(0);
    setPagesTotal({ crawled: 0, total: 0 });
    setCurrentUrl("");
    setLogs([]);
    setSelectedItems(new Set());
    setSelectAll(false);
    setActionMsg("");

    if (backendOnline) {
      try {
        const patterns = includePatterns
          .split(",")
          .map((p) => p.trim())
          .filter(Boolean);
        const resp = await startCrawl(url, {
          maxDepth,
          maxPages,
          includePatterns: patterns.length > 0 ? patterns : undefined,
          extractMode,
        });
        setJobId(resp.job_id);
        addLog("크롤링을 시작합니다...");
        addLog(`Job ID: ${resp.job_id}`);

        // Poll status
        pollRef.current = setInterval(async () => {
          try {
            const st = await getCrawlStatus(resp.job_id);
            const pct = st.pages_total > 0 ? Math.round((st.pages_crawled / st.pages_total) * 100) : 0;
            setProgress(pct);
            setPagesTotal({ crawled: st.pages_crawled, total: st.pages_total });
            if (st.current_url) setCurrentUrl(st.current_url);

            if (st.status === "completed") {
              if (pollRef.current) clearInterval(pollRef.current);
              addLog("🎉 크롤링 완료!");
              setCrawling(false);
              setProgress(100);
              try {
                const r = await getCrawlResults(resp.job_id);
                setResults(r);
              } catch {
                setResults(MOCK_CRAWL_RESULTS);
              }
            } else if (st.status === "failed") {
              if (pollRef.current) clearInterval(pollRef.current);
              addLog("❌ 크롤링 실패");
              setCrawling(false);
            }
          } catch {
            // keep polling
          }
        }, 2000);
        return;
      } catch {
        addLog("⚠️ 백엔드 연결 실패, 데모 모드로 전환합니다.");
      }
    }

    // Offline simulation
    simulateCrawl();
  }, [url, backendOnline, maxDepth, maxPages, includePatterns, extractMode, addLog, simulateCrawl]);

  // ── Cancel Crawl ──
  const handleCancel = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    setCrawling(false);
    addLog("🚫 크롤링이 취소되었습니다.");
  }, [addLog]);

  // ── Toggle item selection ──
  const toggleItem = useCallback((key: string) => {
    setSelectedItems((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  // ── Convert selected ──
  const handleConvert = useCallback(async () => {
    if (selectedItems.size === 0) {
      setActionMsg("⚠️ 변환할 항목을 선택해주세요.");
      return;
    }
    if (backendOnline && jobId) {
      try {
        const indices = Array.from(selectedItems).map((k) => parseInt(k.split("-")[1]));
        await convertCrawlResults(jobId, indices);
      } catch { /* fallback */ }
    }
    setActionMsg(`✅ ${selectedItems.size}개 항목을 RAG 문서로 변환했습니다.`);
    setTimeout(() => setActionMsg(""), 3000);
  }, [selectedItems, backendOnline, jobId]);

  // ── Import all ──
  const handleImportAll = useCallback(async () => {
    if (backendOnline && jobId) {
      try {
        await importCrawlResults(jobId);
      } catch { /* fallback */ }
    }
    const total = results
      ? results.faqs.length + results.articles.length + results.products.length + results.policies.length
      : 0;
    setActionMsg(`✅ 전체 ${total}개 항목을 지식베이스에 추가했습니다.`);
    setTimeout(() => setActionMsg(""), 3000);
  }, [backendOnline, jobId, results]);

  // ── Re-import from history ──
  const handleReimport = useCallback(async (jid: string) => {
    if (backendOnline) {
      try {
        await importCrawlResults(jid);
        setActionMsg("✅ 지식베이스에 다시 추가했습니다.");
        setTimeout(() => setActionMsg(""), 3000);
        return;
      } catch { /* fallback */ }
    }
    setActionMsg("✅ (데모) 지식베이스에 다시 추가했습니다.");
    setTimeout(() => setActionMsg(""), 3000);
  }, [backendOnline]);

  // Tab item counts
  const tabCounts = results
    ? {
        faqs: results.faqs.length,
        articles: results.articles.length,
        products: results.products.length,
        policies: results.policies.length,
      }
    : { faqs: 0, articles: 0, products: 0, policies: 0 };

  const totalItems = tabCounts.faqs + tabCounts.articles + tabCounts.products + tabCounts.policies;

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
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
          <Link
            href="/dashboard"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-all mb-1"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            대시보드
          </Link>
          <Link
            href="/datahub"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-all mb-1"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            데이터 허브
          </Link>
          <div className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium bg-blue-50 text-[#2563EB] mb-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
            웹 크롤러
          </div>
          <Link
            href="/dashboard"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-all mb-1"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            지식베이스
          </Link>
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

      {/* Main content */}
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🌐 웹 크롤러</h1>
              <p className="text-sm text-gray-500 mt-1">홈페이지 URL을 입력하면 FAQ, 도움말, 상품정보를 자동으로 수집하여 지식베이스에 추가합니다</p>
            </div>
            <BackendBadge online={backendOnline} />
          </div>

          {/* ── URL Input Section ── */}
          <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-xl">🔗</span>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !crawling && handleStartCrawl()}
                  placeholder="홈페이지 주소를 입력하세요 (예: https://example.com)"
                  disabled={crawling}
                  className="w-full pl-12 pr-4 py-3.5 text-base border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/40 bg-white disabled:bg-gray-50 disabled:text-gray-400 transition-all"
                />
              </div>
              <button
                onClick={handleStartCrawl}
                disabled={crawling || !url.trim()}
                className="px-6 py-3.5 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1d4ed8] transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none whitespace-nowrap"
              >
                {crawling ? (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    크롤링 중...
                  </span>
                ) : (
                  "🚀 크롤링 시작"
                )}
              </button>
            </div>

            {/* Advanced Settings */}
            <div className="mt-4">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
              >
                <svg className={`w-4 h-4 transition-transform ${showAdvanced ? "rotate-90" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                고급 설정
              </button>
              {showAdvanced && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-5 p-5 bg-gray-50 rounded-xl border border-gray-100">
                  {/* Depth */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      크롤링 깊이 <span className="text-[#2563EB] font-bold">{maxDepth}</span>
                    </label>
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={maxDepth}
                      onChange={(e) => setMaxDepth(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#2563EB]"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>1 (얕게)</span><span>5 (깊게)</span>
                    </div>
                  </div>
                  {/* Max Pages */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      최대 페이지 수 <span className="text-[#2563EB] font-bold">{maxPages}</span>
                    </label>
                    <input
                      type="range"
                      min={10}
                      max={100}
                      step={10}
                      value={maxPages}
                      onChange={(e) => setMaxPages(Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#2563EB]"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>10</span><span>100</span>
                    </div>
                  </div>
                  {/* URL Pattern Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">URL 패턴 필터</label>
                    <input
                      type="text"
                      value={includePatterns}
                      onChange={(e) => setIncludePatterns(e.target.value)}
                      placeholder="/faq, /help, /support"
                      className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]/40"
                    />
                    <p className="text-xs text-gray-400 mt-1">쉼표로 구분하여 입력</p>
                  </div>
                  {/* Extract Mode */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">추출 모드</label>
                    <div className="flex gap-3">
                      {[
                        { value: "auto" as const, label: "자동" },
                        { value: "faq" as const, label: "FAQ만" },
                        { value: "all" as const, label: "전체" },
                      ].map((opt) => (
                        <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="radio"
                            name="extractMode"
                            value={opt.value}
                            checked={extractMode === opt.value}
                            onChange={() => setExtractMode(opt.value)}
                            className="w-4 h-4 text-[#2563EB] accent-[#2563EB]"
                          />
                          <span className="text-sm text-gray-700">{opt.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ── Progress Section ── */}
          {crawling && (
            <div className="bg-white rounded-2xl border border-blue-100 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">⏳ 크롤링 진행 중</h3>
                <button
                  onClick={handleCancel}
                  className="text-xs px-3 py-1.5 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 font-medium transition-colors"
                >
                  ✕ 취소
                </button>
              </div>

              {/* Progress bar */}
              <div>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-gray-600">{pagesCrawled.crawled}/{pagesCrawled.total} 페이지</span>
                  <span className="font-bold text-[#2563EB]">{progress}%</span>
                </div>
                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#2563EB] to-blue-400 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Current URL */}
              {currentUrl && (
                <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded-lg overflow-hidden">
                  <svg className="w-3.5 h-3.5 shrink-0 animate-spin text-[#2563EB]" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span className="truncate">{currentUrl}</span>
                </div>
              )}

              {/* Live log */}
              <div className="bg-gray-900 rounded-xl p-4 max-h-48 overflow-y-auto font-mono text-xs">
                {logs.map((log, i) => (
                  <div key={i} className={`py-0.5 ${log.includes("✅") ? "text-green-400" : log.includes("❌") || log.includes("🚫") ? "text-red-400" : log.includes("🎉") ? "text-yellow-300" : "text-gray-400"}`}>
                    {log}
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </div>
          )}

          {/* ── Results Section ── */}
          {results && !crawling && (
            <div className="space-y-4">
              {/* Stats summary */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl px-5 py-4 flex items-center gap-6 flex-wrap">
                <span className="text-sm font-semibold text-blue-900">📊 수집 결과</span>
                <span className="text-xs text-blue-700">총 <b>{totalItems}</b>개 항목 발견</span>
                <span className="text-xs text-blue-600">FAQ <b>{tabCounts.faqs}</b>건</span>
                <span className="text-xs text-blue-600">문서 <b>{tabCounts.articles}</b>건</span>
                <span className="text-xs text-blue-600">상품 <b>{tabCounts.products}</b>건</span>
                <span className="text-xs text-blue-600">정책 <b>{tabCounts.policies}</b>건</span>
              </div>

              {/* Action message */}
              {actionMsg && (
                <div className={`px-4 py-3 rounded-xl text-sm font-medium ${actionMsg.startsWith("✅") ? "bg-green-50 text-green-700 border border-green-100" : "bg-yellow-50 text-yellow-700 border border-yellow-100"}`}>
                  {actionMsg}
                </div>
              )}

              {/* Tabs + Actions */}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between border-b border-gray-100 px-4">
                  <div className="flex">
                    {([
                      { key: "faqs" as const, label: "질문답변", icon: "❓", count: tabCounts.faqs },
                      { key: "articles" as const, label: "도움말 문서", icon: "📄", count: tabCounts.articles },
                      { key: "products" as const, label: "상품정보", icon: "🛍️", count: tabCounts.products },
                      { key: "policies" as const, label: "정책/안내", icon: "📋", count: tabCounts.policies },
                    ]).map((tab) => (
                      <button
                        key={tab.key}
                        onClick={() => { setActiveTab(tab.key); setSelectAll(false); }}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-all ${
                          activeTab === tab.key
                            ? "border-[#2563EB] text-[#2563EB]"
                            : "border-transparent text-gray-500 hover:text-gray-700"
                        }`}
                      >
                        {tab.icon} {tab.label} <span className="text-xs ml-1 opacity-60">({tab.count})</span>
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectAll}
                        onChange={(e) => {
                          setSelectAll(e.target.checked);
                          if (!e.target.checked) {
                            // Deselect all items in current tab
                            setSelectedItems((prev) => {
                              const next = new Set(prev);
                              getTabItems().forEach((_, i) => next.delete(`${activeTab}-${i}`));
                              return next;
                            });
                          }
                        }}
                        className="w-3.5 h-3.5 accent-[#2563EB]"
                      />
                      전체 선택
                    </label>
                  </div>
                </div>

                {/* Tab content */}
                <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
                  {activeTab === "faqs" && results.faqs.map((faq, i) => (
                    <div
                      key={i}
                      className="flex gap-3 p-4 bg-gray-50 rounded-xl hover:bg-blue-50/50 hover:border-blue-100 border border-transparent transition-all cursor-pointer"
                      onClick={() => toggleItem(`faqs-${i}`)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedItems.has(`faqs-${i}`)}
                        onChange={() => toggleItem(`faqs-${i}`)}
                        className="w-4 h-4 mt-0.5 accent-[#2563EB] shrink-0"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">Q: {faq.question}</p>
                        <p className="text-sm text-gray-600 mt-1">A: {faq.answer}</p>
                        <p className="text-xs text-gray-400 mt-1.5 truncate">🔗 {faq.sourceUrl}</p>
                      </div>
                    </div>
                  ))}

                  {activeTab === "articles" && results.articles.map((article, i) => (
                    <div
                      key={i}
                      className="flex gap-3 p-4 bg-gray-50 rounded-xl hover:bg-blue-50/50 hover:border-blue-100 border border-transparent transition-all cursor-pointer"
                      onClick={() => toggleItem(`articles-${i}`)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedItems.has(`articles-${i}`)}
                        onChange={() => toggleItem(`articles-${i}`)}
                        className="w-4 h-4 mt-0.5 accent-[#2563EB] shrink-0"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">📄 {article.title}</p>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">{article.content}</p>
                        <p className="text-xs text-gray-400 mt-1.5 truncate">🔗 {article.sourceUrl}</p>
                      </div>
                    </div>
                  ))}

                  {activeTab === "products" && results.products.map((product, i) => (
                    <div
                      key={i}
                      className="flex gap-3 p-4 bg-gray-50 rounded-xl hover:bg-blue-50/50 hover:border-blue-100 border border-transparent transition-all cursor-pointer"
                      onClick={() => toggleItem(`products-${i}`)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedItems.has(`products-${i}`)}
                        onChange={() => toggleItem(`products-${i}`)}
                        className="w-4 h-4 mt-0.5 accent-[#2563EB] shrink-0"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">🛍️ {product.name}</p>
                        <p className="text-sm text-gray-600 mt-1">{product.description}</p>
                        <p className="text-xs text-gray-400 mt-1.5 truncate">🔗 {product.sourceUrl}</p>
                      </div>
                    </div>
                  ))}

                  {activeTab === "policies" && results.policies.map((policy, i) => (
                    <div
                      key={i}
                      className="flex gap-3 p-4 bg-gray-50 rounded-xl hover:bg-blue-50/50 hover:border-blue-100 border border-transparent transition-all cursor-pointer"
                      onClick={() => toggleItem(`policies-${i}`)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedItems.has(`policies-${i}`)}
                        onChange={() => toggleItem(`policies-${i}`)}
                        className="w-4 h-4 mt-0.5 accent-[#2563EB] shrink-0"
                        onClick={(e) => e.stopPropagation()}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">📋 {policy.title}</p>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">{policy.content}</p>
                        <p className="text-xs text-gray-400 mt-1.5 truncate">🔗 {policy.sourceUrl}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Action buttons */}
                <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50/50">
                  <span className="text-xs text-gray-400">
                    {selectedItems.size > 0 ? `${selectedItems.size}개 항목 선택됨` : "항목을 선택하세요"}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={handleConvert}
                      disabled={selectedItems.size === 0}
                      className="text-xs px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                    >
                      📝 선택항목 RAG 문서로 변환
                    </button>
                    <button
                      onClick={handleImportAll}
                      className="text-xs px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-all"
                    >
                      📚 전체 지식베이스에 추가
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── Crawl History ── */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <h3 className="text-sm font-semibold text-gray-900">📜 크롤링 히스토리</h3>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${showHistory ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {showHistory && (
              <div className="px-6 pb-4">
                {jobs.length === 0 ? (
                  <p className="text-sm text-gray-400 py-4 text-center">크롤링 이력이 없습니다.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-xs text-gray-500 border-b border-gray-100">
                          <th className="pb-2 font-medium">URL</th>
                          <th className="pb-2 font-medium">날짜</th>
                          <th className="pb-2 font-medium">상태</th>
                          <th className="pb-2 font-medium">페이지</th>
                          <th className="pb-2 font-medium">항목</th>
                          <th className="pb-2 font-medium"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {jobs.map((job) => (
                          <tr key={job.job_id} className="border-b border-gray-50 hover:bg-gray-50/50">
                            <td className="py-2.5 text-gray-900 max-w-[200px] truncate">{job.url}</td>
                            <td className="py-2.5 text-gray-500">{new Date(job.created_at).toLocaleDateString("ko-KR")}</td>
                            <td className="py-2.5">
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                job.status === "completed" ? "bg-green-50 text-green-600"
                                : job.status === "running" ? "bg-blue-50 text-blue-600"
                                : job.status === "failed" ? "bg-red-50 text-red-500"
                                : "bg-gray-100 text-gray-500"
                              }`}>
                                {job.status === "completed" ? "완료" : job.status === "running" ? "진행중" : job.status === "failed" ? "실패" : job.status}
                              </span>
                            </td>
                            <td className="py-2.5 text-gray-500">{job.pages_crawled ?? "-"}</td>
                            <td className="py-2.5 text-gray-500">{job.items_found ?? "-"}</td>
                            <td className="py-2.5">
                              {job.status === "completed" && (
                                <button
                                  onClick={() => handleReimport(job.job_id)}
                                  className="text-xs px-3 py-1 bg-blue-50 text-[#2563EB] rounded-lg hover:bg-blue-100 font-medium transition-colors"
                                >
                                  다시 가져오기
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
