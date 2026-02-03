"use client";

import type { Analytics } from "@/lib/api";

const MOCK_DAILY_CHART = [
  { day: "Mon", value: 85 }, { day: "Tue", value: 92 }, { day: "Wed", value: 78 },
  { day: "Thu", value: 96 }, { day: "Fri", value: 88 }, { day: "Sat", value: 65 }, { day: "Sun", value: 45 },
];

const MOCK_SATISFACTION_DIST = [
  { stars: 5, count: 847, pct: 66 },
  { stars: 4, count: 265, pct: 21 },
  { stars: 3, count: 102, pct: 8 },
  { stars: 2, count: 41, pct: 3 },
  { stars: 1, count: 25, pct: 2 },
];

interface AnalyticsTabProps {
  analytics: Analytics | null;
}

function AnalyticsTab({ analytics }: AnalyticsTabProps) {
  const hourlyData = analytics?.hourly_data || [
    { hour: "00", v: 12 }, { hour: "03", v: 5 }, { hour: "06", v: 8 },
    { hour: "09", v: 45 }, { hour: "12", v: 62 }, { hour: "15", v: 58 },
    { hour: "18", v: 42 }, { hour: "21", v: 28 },
  ];

  const satisfactionDist = analytics?.satisfaction_distribution || MOCK_SATISFACTION_DIST;
  const aiResolution = analytics?.ai_resolution_rate ?? 87.3;
  const escalationRate = analytics?.escalation_rate ?? 12.7;
  const avgTurns = analytics?.avg_turns ?? 4.2;

  const maxHourly = Math.max(...hourlyData.map((d) => d.v));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        <p className="text-sm text-gray-500 mt-1">Analyze customer support performance and identify improvement opportunities</p>
      </div>

      {/* KPI Cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">AI Resolution Rate</div>
          <div className="text-3xl font-bold text-gray-900">{aiResolution}%</div>
          <div className="mt-2 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-green-500 rounded-full" style={{ width: `${aiResolution}%` }} />
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Escalation Rate</div>
          <div className="text-3xl font-bold text-gray-900">{escalationRate}%</div>
          <div className="mt-2 w-full h-2 bg-orange-500 rounded-full overflow-hidden">
            <div className="h-full bg-orange-500 rounded-full" style={{ width: `${escalationRate}%` }} />
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Avg Turns per Conversation</div>
          <div className="text-3xl font-bold text-gray-900">{avgTurns}회</div>
          <div className="mt-2 w-full h-2 bg-[#2563EB] rounded-full overflow-hidden">
            <div className="h-full bg-[#2563EB] rounded-full" style={{ width: `${(avgTurns / 10) * 100}%` }} />
          </div>
        </div>
      </div>

      {/* Hourly Chart */}
      <div className="bg-white p-6 rounded-xl border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Hourly Message Volume</h3>
        <div className="flex items-end gap-3 h-48">
          <div className="flex items-end gap-2">
            {hourlyData.map((d) => (
              <div key={d.hour} className="flex-1 flex flex-col items-center gap-2">
                <span className="text-xs text-gray-400 font-medium">{d.v}</span>
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
      </div>

      {/* Satisfaction Distribution */}
      <div className="bg-white p-6 rounded-xl border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Satisfaction Distribution</h3>
        <div className="space-y-3">
          {satisfactionDist.map((row) => (
            <div key={row.stars} className="flex items-center gap-3">
              <div className="flex gap-0.5 w-20 shrink-0">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span key={i} className={`text-sm ${i < row.stars ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                ))}
              </div>
              <div className="flex-1 flex-col gap-1 flex-1">
                <div className="text-sm font-medium text-gray-900">{row.stars} Stars</div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{row.count} reviews</span>
                  <span className={`text-xs font-medium ${row.pct > 66 ? "text-green-600" : "text-orange-600"}`}>({row.pct}%)</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
