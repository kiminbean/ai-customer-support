import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "위젯 미리보기 - 임베드 가능한 채팅 위젯",
  description: "SupportAI 채팅 위젯을 미리 확인하세요. 간단한 코드 한 줄로 웹사이트에 AI 고객지원을 추가할 수 있습니다.",
  openGraph: {
    title: "위젯 미리보기 | SupportAI",
    description: "SupportAI 채팅 위젯을 미리 확인하세요. 간단한 코드 한 줄로 웹사이트에 AI 고객지원을 추가할 수 있습니다.",
  },
};

export default function WidgetLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
