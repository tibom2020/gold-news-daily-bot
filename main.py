#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold News Daily Bot - Ban tin vang Viet Nam moi ngay.

Chay: python main.py
Cron 08:00: 0 8 * * * cd /path/to/bot && python main.py
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

# Thêm project root vào path
sys.path.insert(0, str(Path(__file__).parent))

from config import MIN_NEWS
from src.analyzer import analyze
from src.delivery import send_n8n, send_telegram
from src.fetcher import fetch_news


def main():
    print("🟡 Gold News Daily Bot — Đang thu thập tin...")
    news = fetch_news()

    if len(news) < MIN_NEWS:
        print(f"⚠️ Chỉ có {len(news)} tin vàng (cần {MIN_NEWS}+). Vẫn tiếp tục...")

    if not news:
        print("❌ Không có tin vàng nào trong 48h qua.")
        return 1

    print(f"✓ Đã lấy {len(news)} tin vàng. Đang phân tích bằng Gemini...")
    try:
        report = analyze(news)
    except Exception as e:
        print(f"❌ Gemini lỗi: {e}")
        return 1

    print("✓ Đã tạo bản tin. Đang gửi...")
    ok_telegram = send_telegram(report)
    ok_n8n = send_n8n(report, len(news))

    if ok_telegram:
        print("✓ Đã gửi Telegram.")
    if ok_n8n or not ok_n8n:
        print("✓ n8n hoàn tất.")

    print("\n--- Bản tin ---\n")
    print(report[:500] + "..." if len(report) > 500 else report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
