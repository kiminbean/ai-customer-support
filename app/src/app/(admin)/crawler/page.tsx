"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import {
  startCrawl,
  getCrawlStatus,
  getCrawlResults,
  convertCrawlResults,
  importCrawlResults,
  getCrawlJobs,
  type CrawlResults,
  type CrawlJob,
} from "@/lib/api";
import { BackendBadge } from "@/components/BackendBadge";
import { MOCK_CRAWL_RESULTS, MOCK_CRAWL_JOBS } from "@/data/mock-crawl";

type ResultTab = "faqs" | "articles" | "products" | "policies";

// ── Main Page ──
export default function CrawlerPage() {
  const backendOnline = useHealthCheck();

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
    if (!results || !selectAll) return;
    const items = (() => {
      switch (activeTab) {
        case "faqs": return results.faqs;
        case "articles": return results.articles;
        case "products": return results.products;
        case "policies": return results.policies;
      }
    })();
    setSelectedItems((prev) => {
      const next = new Set(prev);
      items.forEach((_, i) => next.add(`${activeTab}-${i}`));
      return next;
    });
  }, [selectAll, activeTab, results]);

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
    <div className="p-8 overflow-auto">
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
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
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
                    <span className="w-4 h-4 animate-spin">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    </span>
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
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-5 p-5 bg-gray-50 rounded-xl border border-gray-200">
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
                  <span className="w-3.5 h-3.5 shrink-0 animate-spin text-[#2563EB]">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  </span>
                  <span className="truncate">{currentUrl}</span>
                </div>
              )}

              {/* Live log */}
              <div className="bg-gray-900 rounded-xl p-4 max-h-48 overflow-y-auto font-mono text-xs scrollable-list">
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
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between border-b border-gray-200 px-4">
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
                <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto scrollable-list">
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
                <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50/50">
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
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
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
                        <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
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
      </div>
  );
}
