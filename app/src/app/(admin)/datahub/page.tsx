"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { DashboardSidebar } from "@/components/DashboardSidebar";
import { BackendBadge } from "@/components/BackendBadge";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import {
  getDatahubDomains,
  getDatahubDatasets,
  searchDatahubDatasets,
  downloadDataset,
  getDownloadStatus,
  processDataset,
  getProcessStatus,
  importDataset,
  getImportedDatasets,
  type DatahubDomain,
  type DatahubDataset,
  type DatahubImportedDataset,
} from "@/lib/api";
import { MOCK_DOMAINS, MOCK_DATASETS } from "@/data/mock-datasets";

// ── Status helpers ──

type DatasetStatus = "not_downloaded" | "downloading" | "downloaded" | "processing" | "imported";

function statusLabel(status: DatasetStatus): string {
  switch (status) {
    case "not_downloaded": return "미다운로드";
    case "downloading": return "다운로드 중";
    case "downloaded": return "다운로드 완료";
    case "processing": return "처리 중";
    case "imported": return "가져옴 ✅";
  }
}

function statusColor(status: DatasetStatus): string {
  switch (status) {
    case "not_downloaded": return "bg-gray-100 text-gray-500";
    case "downloading": return "bg-blue-50 text-blue-600";
    case "downloaded": return "bg-green-50 text-green-600";
    case "processing": return "bg-yellow-50 text-yellow-600";
    case "imported": return "bg-emerald-50 text-emerald-700";
  }
}

function formatBadge(format?: string): string {
  switch (format) {
    case "conversation": return "💬 대화";
    case "qa": return "❓ Q&A";
    case "ticket": return "🎫 티켓";
    case "tweet": return "🐦 트윗";
    default: return "📄 기타";
  }
}

// ── Pipeline Visualization ──
function PipelineVisual({ activeStep, progress }: { activeStep: number; progress: number }) {
  const steps = [
    { label: "다운로드", icon: "⬇️" },
    { label: "전처리", icon: "⚙️" },
    { label: "번역(선택)", icon: "🌐" },
    { label: "지식베이스 등록", icon: "📚" },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">📋 데이터 파이프라인</h3>
      <div className="flex items-center gap-2">
        {steps.map((step, i) => (
          <div key={step.label} className="flex items-center flex-1">
            <div className={`flex flex-col items-center flex-1 ${i <= activeStep ? "opacity-100" : "opacity-40"}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all duration-300 ${
                i < activeStep
                  ? "bg-green-100 ring-2 ring-green-300"
                  : i === activeStep
                  ? "bg-blue-100 ring-2 ring-blue-400 animate-pulse"
                  : "bg-gray-100"
              }`}>
                {i < activeStep ? "✅" : step.icon}
              </div>
              <span className="text-[11px] font-medium text-gray-600 mt-1.5 text-center leading-tight">{step.label}</span>
              {i === activeStep && progress > 0 && (
                <div className="w-full mt-1.5 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
            </div>
            {i < steps.length - 1 && (
              <div className={`w-8 h-0.5 mx-1 mt-[-16px] ${i < activeStep ? "bg-green-300" : "bg-gray-200"}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Domain Card ──
function DomainCard({
  domain,
  isActive,
  onClick,
}: {
  domain: DatahubDomain;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-left p-4 rounded-xl border transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 ${
        isActive
          ? "border-[#2563EB] bg-blue-50 shadow-sm shadow-blue-100"
          : "border-gray-200 bg-white hover:border-blue-200"
      }`}
    >
      <div className="text-2xl mb-2">{domain.icon || "📦"}</div>
      <div className="text-sm font-semibold text-gray-900">{domain.domain}</div>
      <div className="text-xs text-gray-500 mt-0.5">{domain.description}</div>
      <div className="mt-2 text-xs font-medium text-[#2563EB]">{domain.count}개 데이터셋</div>
    </button>
  );
}

// ── Dataset Card ──
function DatasetCard({
  dataset,
  onDownload,
  onProcess,
  onImport,
}: {
  dataset: DatahubDataset & { _progress?: number };
  onDownload: () => void;
  onProcess: () => void;
  onImport: () => void;
}) {
  const st = (dataset.status || "not_downloaded") as DatasetStatus;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:border-blue-100">
      {/* Top row: name + badges */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-gray-900">{dataset.name}</h4>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
              dataset.language === "KO" ? "bg-purple-50 text-purple-600" : "bg-sky-50 text-sky-600"
            }`}>
              {dataset.language || "EN"}
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 font-medium">
              {formatBadge(dataset.format)}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1 leading-relaxed">{dataset.description}</p>
        </div>
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 ${statusColor(st)}`}>
          {statusLabel(st)}
        </span>
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-3 mt-3 flex-wrap">
        {dataset.size && (
          <span className="text-[11px] text-gray-400">📊 {dataset.size}</span>
        )}
        {dataset.quality_score != null && (
          <span className="text-[11px] text-yellow-500">
            {"⭐".repeat(dataset.quality_score)}
          </span>
        )}
      </div>

      {/* Use case tags */}
      {dataset.use_cases && dataset.use_cases.length > 0 && (
        <div className="flex gap-1.5 mt-2.5 flex-wrap">
          {dataset.use_cases.map((uc) => (
            <span key={uc} className="text-[10px] px-2 py-0.5 bg-gray-50 text-gray-500 rounded-md">
              {uc}
            </span>
          ))}
        </div>
      )}

      {/* Progress bar */}
      {(st === "downloading" || st === "processing") && (
        <div className="mt-3 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              st === "downloading" ? "bg-blue-500" : "bg-yellow-500"
            }`}
            style={{ width: `${dataset._progress || 0}%` }}
          />
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-50">
        <button
          onClick={onDownload}
          disabled={st !== "not_downloaded"}
          className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
            st === "not_downloaded"
              ? "bg-[#2563EB] text-white hover:bg-[#1d4ed8]"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          }`}
        >
          ⬇️ 다운로드
        </button>
        <button
          onClick={onProcess}
          disabled={st !== "downloaded"}
          className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
            st === "downloaded"
              ? "bg-yellow-500 text-white hover:bg-yellow-600"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          }`}
        >
          ⚙️ 처리
        </button>
        <button
          onClick={onImport}
          disabled={st !== "downloaded" && st !== "processing" && st !== "not_downloaded" ? false : st !== "downloaded"}
          className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
            st === "downloaded"
              ? "bg-green-600 text-white hover:bg-green-700"
              : st === "imported"
              ? "bg-emerald-50 text-emerald-600 cursor-default"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          }`}
        >
          {st === "imported" ? "✅ 등록 완료" : "📚 지식베이스에 추가"}
        </button>
      </div>
    </div>
  );
}

// ── Import Stats Bar ──
function ImportStatsBar({ imported }: { imported: DatahubImportedDataset[] }) {
  const totalDatasets = imported.length;
  const totalQA = imported.reduce((sum, d) => sum + (d.qa_pairs || 0), 0);
  const totalDocs = imported.reduce((sum, d) => sum + (d.documents || 0), 0);

  if (totalDatasets === 0) return null;

  return (
    <div className="bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-100 rounded-xl px-5 py-3 flex items-center gap-6 flex-wrap">
      <span className="text-sm font-semibold text-emerald-800">📊 가져오기 현황</span>
      <span className="text-xs text-emerald-600">총 <b>{totalDatasets}</b>개 데이터셋 가져옴</span>
      {totalQA > 0 && (
        <span className="text-xs text-emerald-600"><b>{totalQA.toLocaleString()}</b>개 Q&A 쌍</span>
      )}
      {totalDocs > 0 && (
        <span className="text-xs text-emerald-600"><b>{totalDocs.toLocaleString()}</b>개 문서</span>
      )}
    </div>
  );
}

// ── Main Page ──
export default function DataHubPage() {
  const backendOnline = useHealthCheck();
  const [domains, setDomains] = useState<DatahubDomain[]>(MOCK_DOMAINS);
  const [datasets, setDatasets] = useState<(DatahubDataset & { _progress?: number })[]>(MOCK_DATASETS);
  const [imported, setImported] = useState<DatahubImportedDataset[]>([]);
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<DatahubDataset[] | null>(null);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load from backend
  useEffect(() => {
    if (!backendOnline) return;
    (async () => {
      try {
        const [doms, dsets, imp] = await Promise.all([
          getDatahubDomains().catch(() => null),
          getDatahubDatasets().catch(() => null),
          getImportedDatasets().catch(() => []),
        ]);
        if (doms) setDomains(doms);
        if (dsets) setDatasets(dsets);
        setImported(imp);
      } catch {
        // fallback to mock
      }
    })();
  }, [backendOnline]);

  // Filter datasets by domain
  const handleDomainClick = useCallback(async (domain: string) => {
    if (activeDomain === domain) {
      setActiveDomain(null);
      setSearchResults(null);
      return;
    }
    setActiveDomain(domain);
    setSearchQuery("");
    setSearchResults(null);
    if (backendOnline) {
      try {
        const filtered = await getDatahubDatasets(domain);
        setSearchResults(filtered);
        return;
      } catch {
        // fallback
      }
    }
    // Client-side filter
    setSearchResults(datasets.filter((d) => d.domain === domain));
  }, [activeDomain, backendOnline, datasets]);

  // Search
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setActiveDomain(null);
    if (backendOnline) {
      try {
        const results = await searchDatahubDatasets(searchQuery);
        setSearchResults(results);
        return;
      } catch {
        // fallback
      }
    }
    const q = searchQuery.toLowerCase();
    setSearchResults(
      datasets.filter(
        (d) =>
          d.name.toLowerCase().includes(q) ||
          (d.description || "").toLowerCase().includes(q) ||
          (d.domain || "").toLowerCase().includes(q)
      )
    );
  }, [searchQuery, backendOnline, datasets]);

  // Polling helper
  const pollJob = useCallback(
    (
      datasetId: string,
      jobId: string,
      type: "download" | "process",
      onComplete: () => void
    ) => {
      const statusFn = type === "download" ? getDownloadStatus : getProcessStatus;
      const statusField = type === "download" ? "downloading" : "processing";
      const stepIdx = type === "download" ? 0 : 1;
      setPipelineStep(stepIdx);

      if (pollRef.current) clearInterval(pollRef.current);
      pollRef.current = setInterval(async () => {
        try {
          const st = await statusFn(jobId);
          setPipelineProgress(st.progress || 0);
          setDatasets((prev) =>
            prev.map((d) =>
              d.id === datasetId
                ? { ...d, status: statusField as DatasetStatus, _progress: st.progress || 0 }
                : d
            )
          );
          if (st.status === "completed" || st.progress >= 100) {
            if (pollRef.current) clearInterval(pollRef.current);
            onComplete();
          } else if (st.status === "error") {
            if (pollRef.current) clearInterval(pollRef.current);
            setPipelineStep(-1);
          }
        } catch {
          // keep polling
        }
      }, 2000);
    },
    []
  );

  // Simulate progress when offline
  const simulateProgress = useCallback(
    (
      datasetId: string,
      statusDuring: DatasetStatus,
      statusAfter: DatasetStatus,
      stepIdx: number,
      durationMs: number
    ) => {
      setPipelineStep(stepIdx);
      let progress = 0;
      const tick = durationMs / 20;
      const interval = setInterval(() => {
        progress += 5;
        setPipelineProgress(progress);
        setDatasets((prev) =>
          prev.map((d) =>
            d.id === datasetId ? { ...d, status: statusDuring, _progress: progress } : d
          )
        );
        if (progress >= 100) {
          clearInterval(interval);
          setDatasets((prev) =>
            prev.map((d) =>
              d.id === datasetId ? { ...d, status: statusAfter, _progress: 100 } : d
            )
          );
          setPipelineStep(-1);
          setPipelineProgress(0);
        }
      }, tick);
    },
    []
  );

  // Download handler
  const handleDownload = useCallback(
    async (datasetId: string) => {
      setDatasets((prev) =>
        prev.map((d) => (d.id === datasetId ? { ...d, status: "downloading" as DatasetStatus, _progress: 0 } : d))
      );
      if (backendOnline) {
        try {
          const { job_id } = await downloadDataset(datasetId);
          pollJob(datasetId, job_id, "download", () => {
            setDatasets((prev) =>
              prev.map((d) =>
                d.id === datasetId ? { ...d, status: "downloaded" as DatasetStatus, _progress: 100 } : d
              )
            );
            setPipelineStep(-1);
            setPipelineProgress(0);
          });
          return;
        } catch {
          // fallback to simulation
        }
      }
      simulateProgress(datasetId, "downloading", "downloaded", 0, 3000);
    },
    [backendOnline, pollJob, simulateProgress]
  );

  // Process handler
  const handleProcess = useCallback(
    async (datasetId: string) => {
      setDatasets((prev) =>
        prev.map((d) => (d.id === datasetId ? { ...d, status: "processing" as DatasetStatus, _progress: 0 } : d))
      );
      if (backendOnline) {
        try {
          const { job_id } = await processDataset(datasetId, true);
          pollJob(datasetId, job_id, "process", () => {
            setDatasets((prev) =>
              prev.map((d) =>
                d.id === datasetId ? { ...d, status: "downloaded" as DatasetStatus, _progress: 100 } : d
              )
            );
            setPipelineStep(-1);
            setPipelineProgress(0);
          });
          return;
        } catch {
          // fallback
        }
      }
      simulateProgress(datasetId, "processing", "downloaded", 1, 4000);
    },
    [backendOnline, pollJob, simulateProgress]
  );

  // Import handler
  const handleImport = useCallback(
    async (datasetId: string) => {
      if (backendOnline) {
        try {
          await importDataset(datasetId);
        } catch {
          // fallback
        }
      }
      setPipelineStep(3);
      setPipelineProgress(100);
      setDatasets((prev) =>
        prev.map((d) => (d.id === datasetId ? { ...d, status: "imported" as DatasetStatus, _progress: 100 } : d))
      );
      const ds = datasets.find((d) => d.id === datasetId);
      setImported((prev) => [
        ...prev,
        {
          dataset_id: datasetId,
          name: ds?.name,
          imported_at: new Date().toISOString(),
          qa_pairs: Math.floor(Math.random() * 5000) + 500,
          documents: Math.floor(Math.random() * 200) + 50,
        },
      ]);
      setTimeout(() => {
        setPipelineStep(-1);
        setPipelineProgress(0);
      }, 1500);
    },
    [backendOnline, datasets]
  );

  const displayDatasets = searchResults || datasets;
  const filteredDisplay = activeDomain && !searchResults
    ? displayDatasets.filter((d) => d.domain === activeDomain)
    : displayDatasets;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <DashboardSidebar activePage="datahub" backendOnline={backendOnline} />

      {/* Main content */}
      <main className="flex-1 p-8 overflow-auto">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">📦 데이터 허브</h1>
              <p className="text-sm text-gray-500 mt-1">도메인별 고품질 고객지원 데이터를 다운로드하여 AI 지식베이스를 강화하세요</p>
            </div>
            <BackendBadge online={backendOnline} />
          </div>

          {/* Search bar */}
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="데이터셋 검색... (이름, 설명, 도메인)"
              className="flex-1 px-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30 bg-white"
            />
            <button
              onClick={handleSearch}
              className="px-5 py-2.5 bg-[#2563EB] text-white text-sm font-medium rounded-xl hover:bg-[#1d4ed8] transition-colors"
            >
              🔍 검색
            </button>
            {(searchResults || activeDomain) && (
              <button
                onClick={() => {
                  setSearchResults(null);
                  setActiveDomain(null);
                  setSearchQuery("");
                }}
                className="px-4 py-2.5 bg-gray-100 text-gray-600 text-sm font-medium rounded-xl hover:bg-gray-200 transition-colors"
              >
                ✕ 초기화
              </button>
            )}
          </div>

          {/* Import Stats */}
          <ImportStatsBar imported={imported} />

          {/* Pipeline */}
          {pipelineStep >= 0 && <PipelineVisual activeStep={pipelineStep} progress={pipelineProgress} />}

          {/* Domain Cards Grid */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">🏷️ 도메인별 탐색</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {domains.map((d) => (
                <DomainCard
                  key={d.domain}
                  domain={d}
                  isActive={activeDomain === d.domain}
                  onClick={() => handleDomainClick(d.domain)}
                />
              ))}
            </div>
          </div>

          {/* Dataset List */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900">
                📋 데이터셋 목록
                {activeDomain && <span className="text-[#2563EB] ml-2">— {activeDomain}</span>}
                {searchQuery && searchResults && <span className="text-[#2563EB] ml-2">— &quot;{searchQuery}&quot; 검색 결과</span>}
              </h3>
              <span className="text-xs text-gray-400">{filteredDisplay.length}개</span>
            </div>
            <div className="grid gap-4 md:grid-cols-2 scrollable-list">
              {filteredDisplay.length === 0 ? (
                <div className="col-span-2 text-center py-12 text-gray-400 text-sm">
                  해당하는 데이터셋이 없습니다.
                </div>
              ) : (
                filteredDisplay.map((ds) => (
                  <DatasetCard
                    key={ds.id}
                    dataset={ds}
                    onDownload={() => handleDownload(ds.id)}
                    onProcess={() => handleProcess(ds.id)}
                    onImport={() => handleImport(ds.id)}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}