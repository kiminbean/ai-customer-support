"use client";

import type { Conversation } from "@/lib/api";

interface ConversationsTabProps {
  conversations: Conversation[];
  isLoading: boolean;
}

const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "1", user: "김서연", avatar: "KS", last_message: "주문한 상품의 배송 상태를 확인하고 싶어요", time: "2분 전", status: "진행중", satisfaction: null },
  { id: "2", user: "이준호", avatar: "LJ", last_message: "반품 절차가 어떻게 되나요?", time: "15분 전", status: "완료", satisfaction: 5 },
  { id: "3", user: "박민지", avatar: "PM", last_message: "쿠폰 코드가 작동하지 않습니다", time: "32분 전", status: "완료", satisfaction: 4 },
  { id: "4", user: "정하늘", avatar: "JH", last_message: "회원가입 시 혜택이 뭔가요?", time: "1시간 전", status: "완료", satisfaction: 5 },
  { id: "5", user: "최우진", avatar: "CW", last_message: "결제 시 오류가 발생합니다", time: "1시간 전", status: "상담원 전환", satisfaction: 3 },
  { id: "6", user: "강예진", avatar: "KY", last_message: "포인트 적립 기준이 궁금합니다", time: "2시간 전", status: "완료", satisfaction: 5 },
  { id: "7", user: "윤도현", avatar: "YD", last_message: "주문 취소는 어떻게 하나요?", time: "3시간 전", status: "완료", satisfaction: 4 },
];

const STATUS_COLORS = {
  "진행중": "bg-blue-50 text-[#2563EB]",
  "완료": "bg-green-50 text-green-600",
  "상담원 전환": "bg-orange-50 text-orange-600",
};

function ConversationsTab({ conversations, isLoading }: ConversationsTabProps) {
  const displayConversations = conversations.length > 0 ? conversations : MOCK_CONVERSATIONS;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Conversations</h2>
          <p className="text-sm text-gray-500 mt-1">View and manage all customer conversations</p>
        </div>
        <div className="flex gap-2">
          <input type="text" placeholder="Search..." className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30" />
          <select className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/30 focus:border-[#2563EB]/30 bg-white">
            <option>All statuses</option>
            <option>In Progress</option>
            <option>Completed</option>
            <option>Escalated</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Customer</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Last message</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Status</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Rating</th>
              <th className="text-left text-xs font-medium text-gray-500 px-6 py-3">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="px-6 py-3.5">
                    <div className="w-8 h-8 rounded-full bg-gray-200" />
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="w-40 h-4 bg-gray-200 rounded mb-2" />
                    <div className="w-24 h-3 bg-gray-100 rounded" />
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="w-16 h-5 bg-gray-200 rounded-full" />
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="w-20 h-4 bg-gray-100 rounded" />
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="w-12 h-3 bg-gray-100 rounded" />
                  </td>
                </tr>
              ))
            ) : (
              displayConversations.map((conv) => (
                <tr key={conv.id} className="hover:bg-gray-50/50 cursor-pointer transition-colors">
                  <td className="px-6 py-3.5">
                    <div className="w-9 h-9 rounded-full bg-[#2563EB] flex items-center justify-center text-white text-xs font-bold">
                      {conv.avatar || conv.user?.slice(0, 2) || "?"}
                    </div>
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="flex flex-col gap-2">
                      <span className="text-sm font-medium text-gray-900">{conv.user || `Conversation #${conv.id}`}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        conv.status === "진행중" ? "bg-blue-50 text-[#2563EB]"
                        : conv.status === "완료" ? "bg-green-50 text-green-600"
                        : "bg-orange-50 text-orange-600"
                      }`}>{conv.status}</span>
                    </div>
                    <p className="text-xs text-gray-500 truncate max-w-[300px]">{conv.last_message}</p>
                  </td>
                  <td className="px-6 py-3.5">
                    <span className={STATUS_COLORS[conv.status as keyof typeof STATUS_COLORS] || "text-gray-400"}>
                      {conv.status}
                    </span>
                  </td>
                  <td className="px-6 py-3.5">
                    {conv.satisfaction != null ? (
                      <div className="flex gap-0.5 justify-end">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <span key={i} className={`text-sm ${i < conv.satisfaction! ? "text-yellow-400" : "text-gray-200"}`}>★</span>
                        ))}
                      </div>
                    ) : <span className="text-xs text-gray-400">—</span>}
                  </td>
                  <td className="px-6 py-3.5 text-gray-400">{conv.time}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ConversationsTab;
