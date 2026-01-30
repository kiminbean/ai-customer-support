"""
웹 크롤러 모듈 — 홈페이지 FAQ/고객지원 콘텐츠 자동 추출

사용자가 웹사이트 URL을 입력하면:
1. 사이트를 크롤링하여 페이지 수집 (scraper)
2. FAQ, 상품정보, 정책 등 고객지원 콘텐츠 추출 (extractor)
3. RAG 문서로 변환하여 지식베이스에 추가 (rag_converter)
"""

from crawler.scraper import WebCrawler, CrawlConfig, CrawledPage
from crawler.extractor import ContentExtractor, ExtractedContent
from crawler.rag_converter import RAGConverter, RAGDocument
from crawler.demo import get_demo_results, get_demo_documents

__all__ = [
    "WebCrawler",
    "CrawlConfig",
    "CrawledPage",
    "ContentExtractor",
    "ExtractedContent",
    "RAGConverter",
    "RAGDocument",
    "get_demo_results",
    "get_demo_documents",
]
