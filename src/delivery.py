"""Gửi bản tin qua Telegram và/hoặc n8n webhook."""
from datetime import datetime

import requests

from config import N8N_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _escape_telegram_markdown(text: str) -> str:
    """Escape ký tự đặc biệt cho Telegram MarkdownV2."""
    # Dùng HTML thay vì MarkdownV2 để đơn giản
    return text


def send_telegram(content: str) -> bool:
    """Gửi bản tin qua Telegram Bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Chưa cấu hình TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram giới hạn 4096 ký tự/message
    if len(content) > 4000:
        parts = [content[i : i + 4000] for i in range(0, len(content), 4000)]
        for part in parts:
            _send_one(url, part)
        return True

    return _send_one(url, content)


def _send_one(url: str, text: str) -> bool:
    """Gửi 1 message."""
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"[X] Telegram loi: {e}")
        return False


def send_n8n(content: str, news_count: int = 0) -> bool:
    """Gửi payload tới n8n webhook."""
    if not N8N_WEBHOOK_URL:
        return True  # Không cấu hình = bỏ qua

    payload = {
        "content": content,
        "news_count": news_count,
        "date": datetime.now().isoformat(),
    }
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ n8n webhook lỗi: {e}")
        return False
