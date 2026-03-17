"""Tổng hợp giá vàng trong nước từ 3 nguồn chính thống: SJC, PNJ, DOJI."""
import requests

# vang.today API - tổng hợp từ nguồn chính thống, cập nhật mỗi 5 phút
# https://www.vang.today/vi/api
VANG_TODAY_API = "https://www.vang.today/api/prices"

# Mã loại vàng tương ứng 3 nguồn chính
GOLD_SOURCES = {
    "SJC": "SJL1L10",      # SJC 9999 - Công ty Vàng bạc Đá quý Sài Gòn
    "PNJ": "PQHN24NTT",    # PNJ 24K - Công ty Vàng bạc Đá quý Phú Nhuận
    "DOJI": "DOHNL",       # DOJI Hà Nội - Tập đoàn Vàng bạc Đá quý DOJI
}


def _format_vnd(value: int) -> str:
    """Format số tiền VND (triệu đồng/lượng)."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} tr"
    return f"{value:,} đ"


def fetch_gold_prices() -> dict | None:
    """
    Lấy giá vàng mua/bán từ 3 nguồn: SJC, PNJ, DOJI.
    Trả về dict hoặc None nếu lỗi.
    """
    try:
        r = requests.get(
            VANG_TODAY_API,
            headers={"User-Agent": "GoldNewsBot/1.0"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    if not data.get("success") or "prices" not in data:
        return None

    prices = data["prices"]
    result = {
        "sources": [],
        "world_gold_usd": None,
        "updated": data.get("time", ""),
        "date": data.get("date", ""),
    }

    # Vàng thế giới (XAU/USD)
    if "XAUUSD" in prices:
        xau = prices["XAUUSD"]
        result["world_gold_usd"] = {
            "buy": xau.get("buy"),
            "change": xau.get("change_buy"),
        }

    # 3 nguồn chính: SJC, PNJ, DOJI
    for name, code in GOLD_SOURCES.items():
        if code not in prices:
            continue
        p = prices[code]
        result["sources"].append({
            "name": name,
            "full_name": p.get("name", name),
            "buy": p.get("buy"),
            "sell": p.get("sell"),
            "change_buy": p.get("change_buy"),
            "change_sell": p.get("change_sell"),
        })

    return result if result["sources"] else None


def format_gold_prices_for_prompt(prices: dict | None) -> str:
    """Format giá vàng thành chuỗi cho prompt LLM."""
    if not prices:
        return "Không lấy được dữ liệu giá vàng."

    lines = []
    if prices.get("world_gold_usd"):
        w = prices["world_gold_usd"]
        lines.append(f"- Vàng thế giới (XAU/USD): {w.get('buy')} USD/oz (biến động: {w.get('change', 0):+.1f})")

    for s in prices.get("sources", []):
        buy = s.get("buy")
        sell = s.get("sell")
        cb = s.get("change_buy") or 0
        cs = s.get("change_sell") or 0
        if buy and sell:
            change_str = f" (biến động: mua {cb:+,} / bán {cs:+,} VND)" if (cb or cs) else ""
            lines.append(
                f"- {s['name']}: Mua {_format_vnd(buy)} | Bán {_format_vnd(sell)}{change_str}"
            )

    if prices.get("updated"):
        lines.append(f"\n(Cập nhật: {prices['date']} {prices['updated']} - nguồn: vang.today)")

    return "\n".join(lines) if lines else "Không có dữ liệu."
