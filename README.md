# 🟡 Gold News Daily Bot

Bot cá nhân gửi bản tin vàng Việt Nam mỗi ngày lúc 08:00 qua Telegram.

**Deploy:** [https://gold-news-daily-bot.onrender.com](https://gold-news-daily-bot.onrender.com) | Webhook: `/webhook`

## Cài đặt

```bash
cd gold-news-daily-bot
pip install -r requirements.txt
cp .env.example .env
```

## Cấu hình `.env`

| Biến | Mô tả |
|------|-------|
| `GEMINI_API_KEY` | Lấy tại [Google AI Studio](https://aistudio.google.com/apikey) |
| `TELEGRAM_BOT_TOKEN` | Tạo bot qua [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Chat ID của bạn (dùng [@userinfobot](https://t.me/userinfobot)) |
| `N8N_WEBHOOK_URL` | (Optional) URL webhook n8n |

## Chạy thử

```bash
python main.py
```

## Lên lịch 08:00 mỗi ngày

**Windows (Task Scheduler):**
- Tạo task mới → Trigger: Daily 08:00
- Action: `python C:\LINH\New Project\gold-news-daily-bot\main.py`

**Linux/Mac (cron):**
```bash
0 8 * * * cd /path/to/gold-news-daily-bot && python main.py
```

## Nguồn tin

- VnExpress Kinh doanh
- Cafef
- VnEconomy

Tin được lọc theo từ khóa vàng (SJC, vàng miếng, giá vàng...) và chỉ lấy tin ≤ 48h.

---

## Chạy online với n8n

### Bước 1: Deploy bot lên cloud

**Railway** (miễn phí ~500h/tháng):
1. Đăng nhập [railway.app](https://railway.app)
2. New Project → Deploy from GitHub (push code lên repo)
3. Thêm biến môi trường: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (và `WEBHOOK_SECRET` nếu muốn bảo vệ endpoint)
4. Lấy URL (vd: `https://gold-news-daily-bot.onrender.com`)

**Render** (miễn phí):
1. Đăng nhập [render.com](https://render.com)
2. New → Web Service → Connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn server:app`
5. Thêm env vars, lấy URL

### Bước 2: Tạo workflow n8n

1. Mở n8n (cloud hoặc self-hosted)
2. **Import workflow**: File → Import → chọn `n8n-workflow.json`
3. Sửa node "Gọi Gold News Bot": thay `YOUR-APP-URL` bằng URL deploy (vd: `gold-news-xxx.railway.app`)
4. Lưu và **Activate** workflow

Hoặc tạo thủ công:
- **Schedule Trigger** → Cron: `0 8 * * *`, Timezone: `Asia/Ho_Chi_Minh`
- **HTTP Request** → POST → `https://gold-news-daily-bot.onrender.com/webhook`

### Bước 3: Kiểm tra

- Gọi thủ công: `curl -X POST https://your-app.railway.app/webhook`
- Hoặc đợi 08:00 sáng (giờ VN)

---

## Cấu trúc

```
gold-news-daily-bot/
├── main.py           # Chạy local
├── server.py         # Webhook cho n8n (deploy online)
├── config.py
├── Procfile          # Railway/Render
├── src/
│   ├── fetcher.py
│   ├── analyzer.py
│   └── delivery.py
├── requirements.txt
└── .env
```
