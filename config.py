"""Cấu hình Gold News Daily Bot."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# RSS nguồn tin (ưu tiên thị trường VN)
RSS_SOURCES = [
    {"name": "VnExpress Kinh doanh", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
    {"name": "Cafef", "url": "https://cafef.vn/home.rss"},
    {"name": "VnEconomy", "url": "https://vneconomy.vn/rss/"},
]

# Từ khóa lọc tin vàng (tiếng Việt + English)
GOLD_KEYWORDS = [
    "vàng", "gold", "SJC", "giá vàng", "vàng miếng", "vàng 24k", "vàng 18k",
    "ounce", "XAU", "kim loại quý", "đầu tư vàng", "thị trường vàng",
]

# Giới hạn tin (BRIEF-6: 5-7 tin, cho phép 3+ khi ít tin)
MIN_NEWS = 3
MAX_NEWS = 7

# Giới hạn từ (400-600)
MIN_WORDS = 400
MAX_WORDS = 600

# Tin không quá 48h
MAX_AGE_HOURS = 48

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# n8n (optional)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# Bảo vệ webhook (optional) - n8n gửi header X-Webhook-Secret
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
