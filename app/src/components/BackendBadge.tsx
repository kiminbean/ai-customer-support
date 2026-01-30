"use client";

export function BackendBadge({ online }: { online: boolean }) {
  return (
    <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${
      online ? "bg-green-50 text-green-700" : "bg-red-50 text-red-500"
    }`}>
      <span className={`w-2 h-2 rounded-full ${online ? "bg-green-500 animate-pulse" : "bg-red-400"}`} />
      {online ? "백엔드 연결됨" : "오프라인 (데모)"}
    </div>
  );
}
