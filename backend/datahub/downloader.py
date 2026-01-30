"""
데이터 허브 다운로더 — HuggingFace 데이터셋 다운로드

huggingface_hub 라이브러리를 사용하여 데이터셋을 다운로드하며,
라이브러리 미설치 시 requests 기반 폴백을 제공한다.
데모 모드에서는 샘플 데이터를 생성하여 오프라인 테스트를 지원.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

import config

# ── 상수 ───────────────────────────────────────────────────

DATASETS_DIR = config.DATA_DIR / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# ── 다운로드 상태 타입 ────────────────────────────────────

STATUS_PENDING = "pending"
STATUS_DOWNLOADING = "downloading"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CACHED = "cached"


# ── 샘플/데모 데이터 ──────────────────────────────────────

DEMO_SAMPLES: Dict[str, List[Dict]] = {
    "conversation": [
        {
            "customer": "I ordered a laptop 5 days ago but haven't received it yet. Order #12345.",
            "agent": "I apologize for the delay. Let me check your order #12345. It appears there was a shipping delay due to weather conditions. Your package is now in transit and should arrive within 2 business days. I've also applied a 10% discount to your next order as compensation.",
            "category": "배송 지연",
        },
        {
            "customer": "How do I return a defective product?",
            "agent": "I'm sorry to hear about the defective product. You can initiate a return by going to My Orders > Select the item > Click 'Return'. You'll receive a prepaid shipping label within 24 hours. Once we receive the item, a full refund will be processed within 3-5 business days.",
            "category": "반품/환불",
        },
        {
            "customer": "I was charged twice for my subscription. Can you help?",
            "agent": "I sincerely apologize for the double charge. I can see the duplicate payment in our system. I've initiated a refund for the extra charge, which will appear in your account within 3-5 business days. Is there anything else I can help with?",
            "category": "결제 오류",
        },
    ],
    "qa": [
        {
            "question": "What is your return policy?",
            "answer": "We offer a 30-day return policy for all unused items in original packaging. For defective items, returns are accepted within 90 days with full refund.",
            "category": "반품 정책",
        },
        {
            "question": "How long does shipping take?",
            "answer": "Standard shipping takes 5-7 business days. Express shipping is available for 2-3 business days. Free shipping on orders over $50.",
            "category": "배송",
        },
        {
            "question": "How do I cancel my order?",
            "answer": "You can cancel your order within 1 hour of placing it through your account dashboard. After that, please contact customer support for assistance.",
            "category": "주문 취소",
        },
    ],
    "intent-response": [
        {
            "intent": "cancel_order",
            "instruction": "I want to cancel my order",
            "response": "I understand you'd like to cancel your order. Could you please provide your order number? I'll process the cancellation right away.",
            "category": "주문 관리",
        },
        {
            "intent": "track_order",
            "instruction": "Where is my package?",
            "response": "I'd be happy to help track your order. Please share your order number or tracking ID, and I'll look up the latest status for you.",
            "category": "배송 추적",
        },
        {
            "intent": "refund_request",
            "instruction": "I need a refund for my purchase",
            "response": "I'm sorry to hear that. I'll help you with the refund process. Could you tell me the order number and the reason for the refund?",
            "category": "환불",
        },
    ],
    "ticket": [
        {
            "subject": "Cannot login to my account",
            "description": "I've been trying to log in for 2 hours. Password reset email not received.",
            "resolution": "Reset the customer's password manually and verified the email address. The issue was caused by an email filter blocking our reset emails.",
            "priority": "high",
            "category": "계정 문제",
        },
        {
            "subject": "Product arrived damaged",
            "description": "The screen of my new monitor has a crack. Order #67890.",
            "resolution": "Arranged immediate replacement shipment with express delivery. Provided return label for damaged item. Applied 15% loyalty discount.",
            "priority": "high",
            "category": "제품 불량",
        },
    ],
    "tweet": [
        {
            "customer_tweet": "@support My app keeps crashing after the latest update! Please fix this ASAP!",
            "support_reply": "@user We're sorry about the crashes! Our team has identified the issue and a hotfix is being released within the next hour. Please update your app then. DM us if the issue persists.",
            "category": "기술 문제",
        },
        {
            "customer_tweet": "@support Been waiting 30 min on hold. This is ridiculous!",
            "support_reply": "@user We sincerely apologize for the long wait time. We're experiencing higher than usual call volumes. Please DM us your issue and we'll get it resolved within 15 minutes.",
            "category": "서비스 불만",
        },
    ],
}


def _generate_demo_data(dataset_id: str, data_format: str) -> List[Dict]:
    """
    데모용 샘플 데이터를 생성한다.

    Args:
        dataset_id: 데이터셋 ID
        data_format: 데이터 포맷 (conversation, qa, intent-response, ticket, tweet)

    Returns:
        샘플 데이터 리스트
    """
    # audio+text 포맷은 conversation으로 폴백
    effective_format = data_format if data_format in DEMO_SAMPLES else "conversation"
    return DEMO_SAMPLES.get(effective_format, DEMO_SAMPLES["qa"])


# ── HuggingFace 다운로더 ──────────────────────────────────


def _get_dataset_dir(dataset_id: str) -> Path:
    """데이터셋 로컬 저장 경로를 반환한다."""
    safe_name = dataset_id.replace("/", "__")
    return DATASETS_DIR / safe_name


def _is_cached(dataset_id: str) -> bool:
    """이미 다운로드된 데이터셋인지 확인한다."""
    dataset_dir = _get_dataset_dir(dataset_id)
    return dataset_dir.exists() and any(dataset_dir.iterdir())


def download_dataset(
    dataset_id: str,
    split: str = "train",
    data_format: str = "qa",
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    HuggingFace에서 데이터셋을 다운로드한다.

    캐시 존재 시 재다운로드를 건너뛰고, huggingface_hub 미설치 시
    requests 기반 폴백 또는 데모 데이터를 생성한다.

    Args:
        dataset_id: HuggingFace 데이터셋 ID (예: "bitext/Bitext-customer-support-llm-chatbot-training-dataset")
        split: 데이터 분할 (기본: "train")
        data_format: 데이터 포맷 (conversation, qa, intent-response, ticket, tweet)
        progress_callback: 진행 상태 콜백 (상태 메시지, 진행률 0.0~1.0)

    Returns:
        {
            "status": "completed" | "cached" | "failed",
            "dataset_id": str,
            "local_path": str,
            "record_count": int,
            "method": "huggingface_hub" | "requests_api" | "demo",
            "error": str | None,
        }
    """
    dataset_dir = _get_dataset_dir(dataset_id)

    # 캐시 확인
    if _is_cached(dataset_id):
        if progress_callback:
            progress_callback("캐시된 데이터셋 발견", 1.0)
        # 캐시된 레코드 수 확인
        data_file = dataset_dir / "data.json"
        record_count = 0
        if data_file.exists():
            try:
                records = json.loads(data_file.read_text(encoding="utf-8"))
                record_count = len(records)
            except Exception as e:
                logger.warning("캐시 데이터 로드 실패 (%s): %s", dataset_id, e)
        return {
            "status": STATUS_CACHED,
            "dataset_id": dataset_id,
            "local_path": str(dataset_dir),
            "record_count": record_count,
            "method": "cache",
            "error": None,
        }

    dataset_dir.mkdir(parents=True, exist_ok=True)

    # 방법 1: huggingface_hub / datasets 라이브러리 사용
    try:
        return _download_via_hf_datasets(dataset_id, split, dataset_dir, progress_callback)
    except ImportError:
        if progress_callback:
            progress_callback("huggingface_hub 미설치, 대체 방법 시도 중...", 0.1)
    except Exception as e:
        if progress_callback:
            progress_callback(f"HF datasets 다운로드 실패: {e}, 폴백 시도...", 0.1)

    # 방법 2: requests 기반 직접 API 호출
    try:
        return _download_via_requests(dataset_id, split, dataset_dir, progress_callback)
    except ImportError:
        if progress_callback:
            progress_callback("requests 미설치, 데모 모드로 전환...", 0.2)
    except Exception as e:
        if progress_callback:
            progress_callback(f"API 다운로드 실패: {e}, 데모 데이터 생성...", 0.2)

    # 방법 3: 데모 데이터 생성
    return _generate_demo_download(dataset_id, data_format, dataset_dir, progress_callback)


def _download_via_hf_datasets(
    dataset_id: str,
    split: str,
    dataset_dir: Path,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """datasets 라이브러리를 사용한 다운로드."""
    from datasets import load_dataset

    if progress_callback:
        progress_callback("HuggingFace datasets 라이브러리로 다운로드 중...", 0.2)

    ds = load_dataset(dataset_id, split=split, trust_remote_code=True)

    if progress_callback:
        progress_callback("데이터 변환 중...", 0.7)

    # pandas DataFrame으로 변환 후 JSON 저장
    records = [dict(row) for row in ds]

    data_file = dataset_dir / "data.json"
    data_file.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 메타데이터 저장
    meta = {
        "dataset_id": dataset_id,
        "split": split,
        "record_count": len(records),
        "columns": list(records[0].keys()) if records else [],
        "method": "huggingface_hub",
        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (dataset_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if progress_callback:
        progress_callback("다운로드 완료", 1.0)

    return {
        "status": STATUS_COMPLETED,
        "dataset_id": dataset_id,
        "local_path": str(dataset_dir),
        "record_count": len(records),
        "method": "huggingface_hub",
        "error": None,
    }


def _download_via_requests(
    dataset_id: str,
    split: str,
    dataset_dir: Path,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """requests 기반 HuggingFace API 직접 호출."""
    import requests

    if progress_callback:
        progress_callback("HuggingFace API로 직접 다운로드 중...", 0.2)

    # HuggingFace datasets API (Parquet 형식)
    api_url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_id}&config=default&split={split}&offset=0&length=100"

    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if progress_callback:
        progress_callback("데이터 파싱 중...", 0.6)

    rows = data.get("rows", [])
    records = [row.get("row", {}) for row in rows]

    if not records:
        raise ValueError("API에서 데이터를 가져올 수 없습니다.")

    # JSON 저장
    data_file = dataset_dir / "data.json"
    data_file.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 메타데이터 저장
    meta = {
        "dataset_id": dataset_id,
        "split": split,
        "record_count": len(records),
        "columns": list(records[0].keys()) if records else [],
        "method": "requests_api",
        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "API를 통해 처음 100개 행만 다운로드됨",
    }
    (dataset_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if progress_callback:
        progress_callback("다운로드 완료", 1.0)

    return {
        "status": STATUS_COMPLETED,
        "dataset_id": dataset_id,
        "local_path": str(dataset_dir),
        "record_count": len(records),
        "method": "requests_api",
        "error": None,
    }


def _generate_demo_download(
    dataset_id: str,
    data_format: str,
    dataset_dir: Path,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """데모용 샘플 데이터를 생성한다."""
    if progress_callback:
        progress_callback("데모 모드: 샘플 데이터 생성 중...", 0.5)

    records = _generate_demo_data(dataset_id, data_format)

    data_file = dataset_dir / "data.json"
    data_file.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    meta = {
        "dataset_id": dataset_id,
        "split": "demo",
        "record_count": len(records),
        "columns": list(records[0].keys()) if records else [],
        "method": "demo",
        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "데모 모드 — 오프라인 샘플 데이터",
    }
    (dataset_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if progress_callback:
        progress_callback("데모 데이터 생성 완료", 1.0)

    return {
        "status": STATUS_COMPLETED,
        "dataset_id": dataset_id,
        "local_path": str(dataset_dir),
        "record_count": len(records),
        "method": "demo",
        "error": None,
    }


# ── 캐시 관리 ─────────────────────────────────────────────


def get_download_info(dataset_id: str) -> Optional[Dict]:
    """다운로드된 데이터셋의 메타데이터를 반환한다."""
    dataset_dir = _get_dataset_dir(dataset_id)
    meta_file = dataset_dir / "metadata.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("메타데이터 로드 실패 (%s): %s", dataset_id, e)
            return None
    return None


def get_downloaded_data(dataset_id: str) -> Optional[List[Dict]]:
    """다운로드된 데이터를 로드하여 반환한다."""
    dataset_dir = _get_dataset_dir(dataset_id)
    data_file = dataset_dir / "data.json"
    if data_file.exists():
        try:
            return json.loads(data_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("다운로드 데이터 로드 실패 (%s): %s", dataset_id, e)
            return None
    return None


def clear_cache(dataset_id: Optional[str] = None) -> Dict[str, Any]:
    """
    다운로드 캐시를 삭제한다.

    Args:
        dataset_id: 특정 데이터셋만 삭제 (None이면 전체 삭제)

    Returns:
        삭제 결과
    """
    import shutil

    if dataset_id:
        dataset_dir = _get_dataset_dir(dataset_id)
        if dataset_dir.exists():
            shutil.rmtree(dataset_dir)
            return {"cleared": 1, "dataset_id": dataset_id}
        return {"cleared": 0, "message": "캐시를 찾을 수 없습니다."}
    else:
        count = 0
        if DATASETS_DIR.exists():
            for child in DATASETS_DIR.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                    count += 1
        return {"cleared": count, "message": f"{count}개 데이터셋 캐시가 삭제되었습니다."}
