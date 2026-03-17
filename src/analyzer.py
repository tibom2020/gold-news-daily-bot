"""Phân tích và tạo bản tin bằng Gemini."""
import json
from datetime import datetime

import google.generativeai as genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_NEWS,
    MAX_WORDS,
    MIN_NEWS,
    MIN_WORDS,
)


SYSTEM_PROMPT = """Bạn là chuyên gia phân tích thị trường vàng Việt Nam, biên tập viên bản tin tài chính.
Giọng điệu trung lập, rõ ràng, ưu tiên dữ liệu và nguồn đáng tin cậy.
Tập trung vào thị trường vàng VIỆT NAM (SJC, vàng miếng, vàng 24K, doanh nghiệp vàng...).
Có thể đề cập bối cảnh quốc tế (giá vàng thế giới, USD) để giải thích biến động trong nước."""

OUTPUT_TEMPLATE = """Tạo bản tin theo ĐÚNG format sau (Tiếng Việt):

### 🟡 BẢN TIN VÀNG NGÀY [DD/MM/YYYY]

**1. Tổng quan giá vàng**
BẮT BUỘC dùng dữ liệu giá vàng được cung cấp bên dưới (SJC, PNJ, DOJI). Format:
- Bảng giá mua/bán từ 3 nguồn SJC, PNJ, DOJI
- Biến động so với phiên trước
- Nhận xét nhanh (1-2 câu)

**2. Tin tức nổi bật**
1. [Tiêu đề tin]
   - Tóm tắt: ...
   - Tác động: ...
   - Nguồn: [link]

(lặp 5-7 tin, mỗi tin có link nguồn)

**3. Phân tích nhanh**
- 3-5 câu phân tích xu hướng

**4. Yếu tố ảnh hưởng chính**
- Liệt kê 3-5 yếu tố

**5. Nguồn tham khảo**
- Liệt kê 3-5 nguồn (link đầy đủ)

YÊU CẦU:
- Tổng 400-600 từ
- 5-7 tin (hoặc ít hơn nếu dữ liệu ít), ít nhất 3 nguồn khác nhau
- Chỉ dùng tin có trong dữ liệu, không bịa
- Gắn link nguồn cho từng tin"""


def analyze(news: list[dict], gold_prices: dict | None = None) -> str:
    """
    Gửi tin + giá vàng lên Gemini, nhận bản tin đã format.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY trong .env")

    genai.configure(api_key=GEMINI_API_KEY)

    # Chọn 5-7 tin quan trọng nhất (đã sort theo thời gian)
    selected = news[:MAX_NEWS]
    if len(selected) < MIN_NEWS:
        selected = news[:MIN_NEWS] if len(news) >= MIN_NEWS else news

    data_str = json.dumps(selected, ensure_ascii=False, indent=2)
    today = datetime.now().strftime("%d/%m/%Y")

    # Format giá vàng từ 3 nguồn SJC, PNJ, DOJI
    from src.gold_price import format_gold_prices_for_prompt

    gold_str = format_gold_prices_for_prompt(gold_prices)

    user_prompt = f"""DỮ LIỆU GIÁ VÀNG TRONG NƯỚC (3 nguồn chính thống - BẮT BUỘC dùng trong mục 1):

{gold_str}

---

DỮ LIỆU TIN TỨC (chỉ dùng tin có trong đây):

{data_str}

Ngày hôm nay: {today}

{OUTPUT_TEMPLATE}"""

    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )

    response = model.generate_content(
        user_prompt,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.3,
        },
    )

    return response.text
