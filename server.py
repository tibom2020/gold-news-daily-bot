#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold News Daily Bot - Webhook server cho n8n.

Deploy lên Railway/Render → n8n Schedule gọi POST /webhook lúc 08:00.

Chạy local: python server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, request

from config import MIN_NEWS, WEBHOOK_SECRET
from src.analyzer import analyze
from src.delivery import send_n8n, send_telegram
from src.fetcher import fetch_news

app = Flask(__name__)


def run_bot():
    """Chạy logic bot, trả về (report, news_count, success)."""
    from src.gold_price import fetch_gold_prices

    news = fetch_news()
    gold_prices = fetch_gold_prices()
    if not news:
        return None, 0, False

    try:
        report = analyze(news, gold_prices)
    except Exception as e:
        return str(e), len(news), False

    send_telegram(report)
    send_n8n(report, len(news))
    return report, len(news), True


@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    """
    Endpoint cho n8n gọi.
    n8n Schedule (08:00) → HTTP Request: POST https://your-app.railway.app/webhook
    """
    if WEBHOOK_SECRET and request.headers.get("X-Webhook-Secret") != WEBHOOK_SECRET:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    report, news_count, success = run_bot()
    return jsonify({
        "success": success,
        "news_count": news_count,
        "report": report or "",
    })


@app.route("/health")
def health():
    """Health check cho Railway/Render."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(__import__("os").getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
