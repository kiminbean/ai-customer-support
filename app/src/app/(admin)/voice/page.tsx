"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import {
  uploadVoice,
  runVoiceDemo,
  getVoiceJobStatus,
  getVoiceTranscript,
  getVoiceDocument,
  approveVoiceDocument,
  getVoiceJobs,
  type VoiceJobStatus,
  type VoiceTranscript,
  type VoiceDocument,
  type VoiceJob,
} from "@/lib/api";
import { BackendBadge } from "@/components/BackendBadge";

type ResultTab = "transcript" | "document";

export default function VoicePage() {
  const backendOnline = useHealthCheck();

  // Input state
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  // Processing state
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<VoiceJobStatus | null>(null);
  const [progress, setProgress] = useState(0);

  // Results state
  const [transcript, setTranscript] = useState<VoiceTranscript | null>(null);
  const [document, setDocument] = useState<VoiceDocument | null>(null);
  const [activeTab, setActiveTab] = useState<ResultTab>("transcript");
  const [showFullText, setShowFullText] = useState(false);

  // History state
  const [jobs, setJobs] = useState<VoiceJob[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Action feedback
  const [actionMsg, setActionMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load jobs history
  const loadJobs = useCallback(async () => {
    if (backendOnline) {
      try {
        const res = await getVoiceJobs();
        setJobs(res.jobs);
      } catch (e) {
        console.error("Failed to load jobs", e);
      }
    }
  }, [backendOnline]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  // Cleanup poll on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // ── Handlers ──

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    const validTypes = [
      "audio/mpeg",
      "audio/wav",
      "audio/x-m4a",
      "audio/webm",
      "audio/ogg",
      "audio/mp4", // m4a often comes as audio/mp4
    ];
    // Check extension as fallback since mime types can be tricky
    const validExts = [".mp3", ".wav", ".m4a", ".webm", ".ogg"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();

    if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
      setErrorMsg("지원하지 않는 파일 형식입니다. (MP3, WAV, M4A, WebM, OGG)");
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setErrorMsg("파일 크기는 50MB를 초과할 수 없습니다.");
      return;
    }

    setFile(file);
    setErrorMsg("");
  };

  const startPolling = useCallback((jid: string) => {
    if (pollRef.current) clearInterval(pollRef.current);

    setProcessing(true);
    setProgress(0);

    pollRef.current = setInterval(async () => {
      try {
        const status = await getVoiceJobStatus(jid);
        setJobStatus(status);
        setProgress(status.progress);

        if (status.status === "completed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setProcessing(false);
          setProgress(100);
          
          // Fetch results
          try {
            const [transRes, docRes] = await Promise.all([
              getVoiceTranscript(jid),
              getVoiceDocument(jid),
            ]);
            setTranscript(transRes);
            setDocument(docRes);
            loadJobs(); // Refresh history
          } catch {
            setErrorMsg("결과를 불러오는 중 오류가 발생했습니다.");
          }
        } else if (status.status === "failed") {
          if (pollRef.current) clearInterval(pollRef.current);
          setProcessing(false);
          setErrorMsg(status.error_message || "처리에 실패했습니다.");
        }
      } catch (e) {
        console.error("Polling error", e);
        // Don't stop polling on transient errors
      }
    }, 2000);
  }, [loadJobs]);

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setErrorMsg("");
    setJobId(null);
    setJobStatus(null);
    setTranscript(null);
    setDocument(null);
    setActionMsg("");

    try {
      const res = await uploadVoice(file);
      setJobId(res.job_id);
      startPolling(res.job_id);
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "업로드 실패");
    } finally {
      setUploading(false);
    }
  };

  const handleDemo = async () => {
    setUploading(true);
    setErrorMsg("");
    setJobId(null);
    setJobStatus(null);
    setTranscript(null);
    setDocument(null);
    setActionMsg("");
    setFile(null); // Clear file selection for demo

    try {
      const res = await runVoiceDemo();
      setJobId(res.job_id);
      startPolling(res.job_id);
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "데모 실행 실패");
    } finally {
      setUploading(false);
    }
  };

  const handleImport = async () => {
    if (!jobId) return;

    try {
      const res = await approveVoiceDocument(jobId);
      setActionMsg(`✅ ${res.documents_added}개의 문서가 지식베이스에 추가되었습니다.`);
      setTimeout(() => setActionMsg(""), 3000);
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "지식베이스 추가 실패");
    }
  };

  return (
    <div className="p-8 overflow-auto">
      <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🎙️ 음성 분석</h1>
              <p className="text-sm text-gray-500 mt-1">
                통화 녹음 파일이나 음성 메모를 업로드하면 자동으로 STT 전사 및 Q&A 문서를 생성합니다.
              </p>
            </div>
            <BackendBadge online={backendOnline} />
          </div>

          {/* ── Input Section ── */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                dragActive
                  ? "border-[#2563EB] bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".mp3,.wav,.m4a,.webm,.ogg,audio/*"
                onChange={handleFileChange}
              />

              <div className="flex flex-col items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-[#2563EB]">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                
                {file ? (
                  <div className="text-sm">
                    <p className="font-semibold text-gray-900">{file.name}</p>
                    <p className="text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button
                      onClick={() => setFile(null)}
                      className="mt-2 text-xs text-red-500 hover:text-red-600 underline"
                    >
                      제거하기
                    </button>
                  </div>
                ) : (
                  <>
                    <p className="text-gray-600 font-medium">
                      오디오 파일을 드래그하거나 <button onClick={() => fileInputRef.current?.click()} className="text-[#2563EB] hover:underline">클릭하여 선택</button>하세요
                    </p>
                    <p className="text-xs text-gray-400">
                      MP3, WAV, M4A, WebM, OGG (최대 50MB)
                    </p>
                  </>
                )}
              </div>
            </div>

            {errorMsg && (
              <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {errorMsg}
              </div>
            )}

            <div className="mt-6 flex gap-3 justify-end">
              <button
                onClick={handleDemo}
                disabled={uploading || processing}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-all"
              >
                데모 실행
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || uploading || processing}
                className="px-5 py-2.5 text-sm font-medium text-white bg-[#2563EB] rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
              >
                {uploading ? (
                  <>
                    <span className="w-4 h-4 animate-spin rounded-full border-2 border-white/30 border-t-white"></span>
                    업로드 중...
                  </>
                ) : (
                  "분석 시작"
                )}
              </button>
            </div>
          </div>

          {/* ── Processing Status ── */}
          {(processing || (jobId && !processing)) && (
            <div className="bg-white rounded-2xl border border-blue-100 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-900">
                  {processing ? "⏳ 분석 진행 중..." : "✅ 분석 완료"}
                </h3>
                <span className="text-sm font-bold text-[#2563EB]">{progress}%</span>
              </div>
              
              <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    jobStatus?.status === "failed" ? "bg-red-500" : "bg-[#2563EB]"
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>{jobStatus?.current_step || "대기 중..."}</span>
                {jobStatus?.status === "failed" && <span className="text-red-500">실패</span>}
              </div>
            </div>
          )}

          {/* ── Results Section ── */}
          {!processing && transcript && document && (
            <div className="space-y-4">
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                {/* Tabs */}
                <div className="flex border-b border-gray-200">
                  <button
                    onClick={() => setActiveTab("transcript")}
                    className={`flex-1 py-4 text-sm font-medium text-center border-b-2 transition-colors ${
                      activeTab === "transcript"
                        ? "border-[#2563EB] text-[#2563EB]"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    📝 전사 스크립트
                  </button>
                  <button
                    onClick={() => setActiveTab("document")}
                    className={`flex-1 py-4 text-sm font-medium text-center border-b-2 transition-colors ${
                      activeTab === "document"
                        ? "border-[#2563EB] text-[#2563EB]"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    📄 Q&A 문서 미리보기
                  </button>
                </div>

                {/* Content */}
                <div className="p-6">
                  {activeTab === "transcript" && (
                    <div className="space-y-6">
                      {/* Summary info */}
                      <div className="flex gap-4 text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
                        <span>언어: {transcript.transcript.language}</span>
                        <span>시간: {transcript.transcript.duration.toFixed(1)}초</span>
                        <span>세그먼트: {transcript.transcript.segments.length}개</span>
                      </div>

                      {/* Segments */}
                      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                        {transcript.transcript.segments.map((seg, idx) => (
                          <div key={idx} className="flex gap-3">
                            <div className="flex-shrink-0 w-16 text-xs text-gray-400 pt-1">
                              {new Date(seg.start_time * 1000).toISOString().substr(14, 5)}
                            </div>
                            <div className="flex-1">
                              <span className="text-xs font-bold text-gray-700 bg-gray-100 px-1.5 py-0.5 rounded mr-2">
                                {seg.speaker || "Speaker"}
                              </span>
                              <p className="text-sm text-gray-800 mt-1">{seg.text}</p>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Full Text Toggle */}
                      <div>
                        <button
                          onClick={() => setShowFullText(!showFullText)}
                          className="text-xs text-[#2563EB] font-medium hover:underline flex items-center gap-1"
                        >
                          {showFullText ? "전체 텍스트 숨기기" : "전체 텍스트 보기"}
                          <svg className={`w-3 h-3 transition-transform ${showFullText ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        {showFullText && (
                          <div className="mt-3 p-4 bg-gray-50 rounded-xl text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                            {transcript.full_text}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {activeTab === "document" && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold text-gray-900">생성된 Q&A ({document.document.qa_count}개)</h3>
                        <div className="text-xs text-gray-500">
                          신뢰도: {(document.document.confidence * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="grid gap-4">
                        {document.document.qa_pairs.map((qa, idx) => (
                          <div key={idx} className="border border-gray-200 rounded-xl p-4 hover:bg-blue-50/30 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                              <span className="text-xs font-semibold text-[#2563EB] bg-blue-50 px-2 py-0.5 rounded">
                                {qa.category}
                              </span>
                              <span className="text-xs text-gray-400">
                                신뢰도 {(qa.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                            <h4 className="font-semibold text-gray-900 mb-2">Q. {qa.question}</h4>
                            <p className="text-sm text-gray-600">A. {qa.answer}</p>
                          </div>
                        ))}
                      </div>
                      
                      <div className="mt-6 border-t border-gray-200 pt-4">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3">Markdown 미리보기</h4>
                        <pre className="bg-gray-900 text-gray-300 p-4 rounded-xl text-xs font-mono overflow-x-auto">
                          {document.preview}
                        </pre>
                      </div>

                      {/* Action */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                        {actionMsg ? (
                          <span className="text-green-600 text-sm font-medium animate-pulse">{actionMsg}</span>
                        ) : (
                          <span className="text-xs text-gray-500">확인 후 지식베이스에 추가하세요.</span>
                        )}
                        <button
                          onClick={handleImport}
                          className="px-5 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 shadow-lg shadow-green-500/20 transition-all flex items-center gap-2"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          지식베이스에 추가
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ── Job History ── */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <h3 className="text-sm font-semibold text-gray-900">📜 분석 히스토리</h3>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${showHistory ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {showHistory && (
              <div className="px-6 pb-4">
                {jobs.length === 0 ? (
                  <p className="text-sm text-gray-400 py-4 text-center">분석 이력이 없습니다.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
                          <th className="pb-2 font-medium">파일명</th>
                          <th className="pb-2 font-medium">날짜</th>
                          <th className="pb-2 font-medium">상태</th>
                          <th className="pb-2 font-medium">세그먼트</th>
                          <th className="pb-2 font-medium">Q&A</th>
                        </tr>
                      </thead>
                      <tbody>
                        {jobs.map((job) => (
                          <tr key={job.job_id} className="border-b border-gray-50 hover:bg-gray-50/50">
                            <td className="py-2.5 text-gray-900 max-w-[200px] truncate" title={job.source_file}>
                              {job.source_file}
                            </td>
                            <td className="py-2.5 text-gray-500">
                              {new Date(job.created_at).toLocaleDateString("ko-KR")}
                            </td>
                            <td className="py-2.5">
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                job.status === "completed" ? "bg-green-50 text-green-600"
                                : job.status === "processing" || job.status === "transcribing" || job.status === "generating" ? "bg-blue-50 text-blue-600"
                                : job.status === "failed" ? "bg-red-50 text-red-500"
                                : "bg-gray-100 text-gray-500"
                              }`}>
                                {job.status === "completed" ? "완료" 
                                 : job.status === "failed" ? "실패" 
                                 : "진행중"}
                              </span>
                            </td>
                            <td className="py-2.5 text-gray-500">
                              {job.transcript_summary?.segment_count ?? "-"}
                            </td>
                            <td className="py-2.5 text-gray-500">
                              {job.document_summary?.qa_count ?? "-"}
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
