import hashlib
import io
import os
import re
import time

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS

st.set_page_config(page_title="Công cụ tính toán pha chế", page_icon="🧪", layout="centered")


def clean_text_for_tts(text: str) -> str:
    """Loại bỏ ký tự Markdown để giọng đọc tự nhiên hơn."""
    text = re.sub(r"[*_`#>~]", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_to_speech_bytes(text: str) -> bytes:
    """Chuyển văn bản tiếng Việt sang MP3 bytes bằng gTTS."""
    cleaned = clean_text_for_tts(text)
    if not cleaned:
        return b""
    tts = gTTS(text=cleaned, lang="vi", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def get_default_api_key() -> str:
    """Lấy API key từ biến môi trường hoặc Streamlit Secrets."""
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key:
        return env_key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def build_system_instruction(
    season: str,
    volume: float,
    ingredients: dict,
    limits: dict,
    dungmoi: float,
    valid: bool,
) -> str:
    """Tạo system instruction kèm thông số pha chế hiện tại trên giao diện."""
    lines = [
        f"- {limits[name]['clean']}: {val:.1f}% (giới hạn tối đa {limits[name]['max']}%)"
        for name, val in ingredients.items()
    ]
    formula_summary = "\n".join(lines)
    total_oil = sum(ingredients.values())
    status_text = "Hợp lệ (được gửi GV duyệt)" if valid else "Chưa hợp lệ"

    return f"""Bạn là trợ lý AI chuyên tư vấn về pha chế nước hoa và nồng độ tinh dầu bằng tiếng Việt.
Hãy trả lời ngắn gọn, dễ hiểu, thân thiện và thực tế để phù hợp khi đọc thành giọng nói.

Thông số công thức hiện tại của người dùng trên web:
- Mùa đã chọn: {season}
- Thể tích mẻ: {volume:.1f} mL
- Tổng nồng độ tinh dầu: {total_oil:.2f}%
- Dung môi Ethanol 96%: {dungmoi:.2f}%
- Trạng thái kiểm tra: {status_text}
- Chi tiết từng thành phần:
{formula_summary}

Quy tắc tư vấn:
1. Dựa vào thông số thực tế ở trên để nhận xét sự cân bằng tầng hương (hương đầu: Bưởi, Rasberry; hương giữa: Trà, Hoa Nhài; hương cuối: Amber, Sandalwood, Cedarwood) và mức độ phù hợp với {season}.
2. Nhắc nhở nhẹ nhàng rằng mọi công thức đều cần giáo viên duyệt an toàn trước khi pha chế thực tế, không tự ý khẳng định an toàn tuyệt đối cho da.
3. Nếu người dùng gửi tin nhắn bằng giọng nói (audio), hãy lắng nghe và trả lời trực tiếp câu hỏi trong audio đó."""


def list_available_gemini_models(client: genai.Client) -> list[str]:
    """Lấy danh sách các model Gemini thực tế hỗ trợ generateContent cho API key hiện tại."""
    found = []
    try:
        for m in client.models.list():
            name = getattr(m, "name", "") or ""
            actions = getattr(m, "supported_actions", None) or []
            short_name = name.replace("models/", "")
            if "gemini" in short_name and (not actions or "generateContent" in actions):
                if "embedding" not in short_name and "imagen" not in short_name:
                    found.append(short_name)
    except Exception:
        pass
    return found


def ask_gemini(
    client: genai.Client,
    model_name: str,
    system_instruction: str,
    history: list,
    user_text: str | None = None,
    audio_bytes: bytes | None = None,
) -> str:
    """Gửi hội thoại + (text hoặc audio) tới Gemini API, tự động thử lại và dò model khả dụng nếu gặp 404/503/429."""
    contents = []
    for msg in history[-10:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )

    current_parts = []
    if audio_bytes:
        current_parts.append(
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        )
        current_parts.append(
            types.Part.from_text(
                text="Người dùng vừa nói câu hỏi trong đoạn ghi âm này. Hãy trả lời trực tiếp bằng tiếng Việt."
            )
        )
    elif user_text:
        current_parts.append(types.Part.from_text(text=user_text))

    contents.append(types.Content(role="user", parts=current_parts))

    candidates = [model_name] + [
        m
        for m in ["gemini-flash-lite-latest"]
        if m != model_name
    ]

    dynamic_models = list_available_gemini_models(client)
    for dm in dynamic_models:
        if dm not in candidates:
            candidates.append(dm)

    last_exc = None
    for candidate_model in candidates:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=candidate_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    ),
                )
                return response.text or "Xin lỗi, mình chưa tạo được câu trả lời. Bạn thử lại nhé."
            except Exception as exc:
                last_exc = exc
                err_str = str(exc)
                if any(code in err_str for code in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED")):
                    time.sleep(1.2 * (attempt + 1))
                    continue
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break
                raise
    raise last_exc


# --- Sidebar cấu hình AI ---
with st.sidebar:
    st.header("⚙️ Cấu hình Gemini AI")
    default_api_key = get_default_api_key()
    api_key = st.text_input(
        "Gemini API Key:",
        value=default_api_key,
        type="password",
        help="Lấy API key tại Google AI Studio (aistudio.google.com).",
    )
    model_name = st.selectbox(
        "Chọn mô hình Gemini:",
        ["gemini-flash-lite-latest"],
        index=0,
    )
    auto_play_voice = st.toggle("Tự động phát giọng nói AI", value=True)
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_audio_hash = None
        st.rerun()

# --- Khởi tạo Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Chào bạn! Mình là trợ lý Gemini. Bạn có thể gõ hoặc nhấn micro để hỏi mình về nồng độ tinh dầu và cách phối hương theo mùa nhé.",
            "audio": None,
        }
    ]
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

# 1. Giữ chỗ ở ĐẦU TRANG cho Cảnh báo và Tiêu đề
top_placeholder = st.container()

# 2. Phần 1: Thiết lập cơ bản
st.header("🛠️ 1. Thiết lập cơ bản")
season = st.selectbox("Chọn mùa:", ["❄️ Mùa đông", "🌸 Mùa xuân", "☀️ Mùa hạ", "🍂 Mùa thu"])
volume = st.number_input("🧪 Thể tích của mẻ (mL):", min_value=1.0, max_value=20.0, value=10.0, step=1.0)

# Bộ màu sắc & icon trang trí xung quanh tự động đổi theo mùa
themes = {
    "❄️ Mùa đông": {
        "bg": "linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #f1f5f9 100%)",
        "primary": "#0284c7",
        "secondary": "#38bdf8",
        "border": "#7dd3fc",
        "deco_left": "❄️<br>⛄<br>🌲<br>🧊<br>✨",
        "deco_right": "✨<br>🧊<br>🌲<br>⛄<br>❄️"
    },
    "🌸 Mùa xuân": {
        "bg": "linear-gradient(135deg, #fce4ec 0%, #f8bbd0 50%, #fff1f2 100%)",
        "primary": "#d81b60",
        "secondary": "#f43f5e",
        "border": "#f48fb1",
        "deco_left": "🌸<br>🍓<br>🌷<br>🦋<br>✨",
        "deco_right": "✨<br>🦋<br>🌷<br>🍓<br>🌸"
    },
    "☀️ Mùa hạ": {
        "bg": "linear-gradient(135deg, #fef9c3 0%, #fde047 50%, #ffedd5 100%)",
        "primary": "#ea580c",
        "secondary": "#f59e0b",
        "border": "#fdba74",
        "deco_left": "☀️<br>🍊<br>🌴<br>🍉<br>✨",
        "deco_right": "✨<br>🍉<br>🌴<br>🍊<br>☀️"
    },
    "🍂 Mùa thu": {
        "bg": "linear-gradient(135deg, #fef3c7 0%, #fcd34d 50%, #ffedd5 100%)",
        "primary": "#b45309",
        "secondary": "#d97706",
        "border": "#fbbf24",
        "deco_left": "🍂<br>🍁<br>🍵<br>🌼<br>✨",
        "deco_right": "✨<br>🌼<br>🍵<br>🍁<br>🍂"
    }
}
t = themes[season]

# CSS trang trí nền, khung viền, dải emoji và ÉP MÀU CHỮ TỐI ĐẬM
st.markdown(f"""
<style>
    /* Nền trang web đổi màu rực rỡ theo mùa */
    .stApp {{
        background: {t['bg']};
    }}
    
    /* Dải icon trang trí bên trái và bên phải màn hình */
    .side-deco-left {{
        position: fixed;
        left: 25px;
        top: 25%;
        font-size: 2.2rem;
        line-height: 2.2;
        opacity: 0.75;
        z-index: 0;
        user-select: none;
        text-align: center;
    }}
    .side-deco-right {{
        position: fixed;
        right: 25px;
        top: 25%;
        font-size: 2.2rem;
        line-height: 2.2;
        opacity: 0.75;
        z-index: 0;
        user-select: none;
        text-align: center;
    }}
    
    /* Khung chính ở giữa nổi bật như tấm thiệp */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.96);
        padding: 2.5rem 3rem !important;
        border-radius: 24px;
        border: 3px solid {t['border']};
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }}

    /* ÉP MÀU CHỮ TỐI ĐẬM (#1e293b) CHO TOÀN BỘ THẺ TRONG .block-container (BAO GỒM DANH SÁCH CHAT) */
    .block-container, 
    .block-container p, 
    .block-container span, 
    .block-container label, 
    .block-container li,
    .block-container ul,
    .block-container ol,
    .block-container strong,
    .block-container b,
    .block-container em,
    .block-container h3,
    .block-container h4,
    .block-container .stSlider label p, 
    .block-container div[data-testid="stWidgetLabel"] p,
    .block-container div[data-testid="stMarkdownContainer"] p,
    .block-container div[data-testid="stMarkdownContainer"] li,
    .block-container div[data-testid="stChatMessageContent"] * {{
        color: #1e293b !important;
    }}
    .block-container, 
    .block-container p, 
    .block-container label, 
    .block-container .stSlider label p, 
    .block-container div[data-testid="stWidgetLabel"] p {{
        font-weight: 600 !important;
    }}
    .block-container div[data-testid="stChatMessageContent"] p,
    .block-container div[data-testid="stChatMessageContent"] li {{
        font-weight: 500 !important;
    }}
    .block-container div[data-testid="stChatMessageContent"] strong {{
        font-weight: 700 !important;
    }}

    /* Trả lại màu chữ chuẩn cho các hộp thông báo st.success, st.warning, st.info, st.error */
    .block-container div[data-testid="stAlert"] p,
    .block-container div[data-testid="stAlert"] span {{
        color: inherit !important;
    }}

    /* GIỮ MÀU CHỮ SÁNG RÕ RÀNG TRONG SIDEBAR CẤU HÌNH */
    section[data-testid="stSidebar"] {{
        background-color: #1e293b !important;
    }}
    section[data-testid="stSidebar"] h2 {{
        color: #f8fafc !important;
        border-left: 4px solid {t['secondary']};
        padding-left: 10px;
        margin-top: 0.5rem !important;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: #334155 !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px;
        font-weight: 600 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #475569 !important;
        border-color: {t['secondary']} !important;
    }}

    /* Khung tiêu đề chính */
    .title-box {{
        background: linear-gradient(90deg, {t['primary']}, {t['secondary']});
        color: #ffffff !important;
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.12);
        margin-bottom: 1rem;
    }}

    /* Trang trí các tiêu đề mục 1, 2, 3, 4 trong khung chính */
    .block-container h2 {{
        color: {t['primary']} !important;
        border-left: 6px solid {t['primary']};
        padding-left: 12px;
        margin-top: 1.5rem !important;
        font-weight: 700 !important;
    }}

    /* Làm đẹp bảng hiển thị kết quả trên web */
    table {{
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        background-color: #ffffff !important;
    }}
    th {{
        background-color: {t['primary']} !important;
        color: #ffffff !important;
        text-align: center !important;
        padding: 10px !important;
        font-size: 1.05rem;
    }}
    td {{
        color: #1e293b !important;
        text-align: center !important;
        padding: 8px !important;
        font-weight: 600 !important;
        background-color: #ffffff !important;
    }}

    /* Nút bấm tải xuống đổi màu theo mùa */
    .stDownloadButton > button, .stDownloadButton > button * {{
        width: 100%;
        background: linear-gradient(90deg, {t['primary']}, {t['secondary']});
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 12px;
        border: none;
        padding: 0.7rem 1rem;
        transition: 0.3s;
    }}
    .stDownloadButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }}
</style>

<!-- Hiển thị dải emoji trang trí 2 bên lề -->
<div class="side-deco-left">{t['deco_left']}</div>
<div class="side-deco-right">{t['deco_right']}</div>
""", unsafe_allow_html=True)

# Đưa Cảnh báo và Tiêu đề lên đúng vị trí ĐẦU TRANG
with top_placeholder:
    st.warning("⚠️ Cần giáo viên duyệt an toàn trước khi pha:")
    st.markdown('<div class="title-box">🧪✨ Công cụ tính toán pha chế ✨🌸</div>', unsafe_allow_html=True)

# 3. Phần 2: Điều chỉnh thành phần
st.header("🌿 2. Điều chỉnh thành phần")
st.write("✨ Sử dụng thanh trượt để điều chỉnh các thành phần hương liệu trong giới hạn:")

limits = {
    "🍊 Bưởi": {"clean": "Bưởi", "max": 2.0, "default": 1.0},
    "🍓 Rasberry": {"clean": "Rasberry", "max": 2.0, "default": 1.0},
    "🍵 Trà": {"clean": "Trà", "max": 2.0, "default": 1.0},
    "🌼 Hoa Nhài": {"clean": "Hoa Nhài", "max": 2.0, "default": 1.0},
    "✨ Amber": {"clean": "Amber", "max": 2.0, "default": 1.0},
    "🪵 Sandalwood": {"clean": "Sandalwood", "max": 2.0, "default": 1.0},
    "🌲 Cedarwood": {"clean": "Cedarwood", "max": 2.0, "default": 1.0},
}

ingredients = {}
for name, config in limits.items():
    ingredients[name] = st.slider(
        f"{name} (≤ {config['max']}%)",
        min_value=0.0,
        max_value=config['max'],
        value=config["default"],
        step=0.1
    )

total = sum(ingredients.values())
dungmoi = 100.0 - total

# 4. Phần 3: Kết quả & Kiểm tra
st.header("📊 3. Kết quả & Kiểm tra")
valid = True
if dungmoi < 0:
    st.error(f"❌ Lỗi: Dung môi bị âm ({dungmoi:.2f}%)")
    valid = False
for name, val in ingredients.items():
    if val > limits[name]["max"]:
        st.error(f"❌ Lỗi: {name} Vượt giới hạn!")
        valid = False

if valid:
    st.success("✅ Trạng thái: ĐƯỢC GỬI GV DUYỆT")

    data_web = {
        "Thành phần": list(ingredients.keys()) + ["💧 Ethanol 96%"],
        "Phần trăm (%)": list(ingredients.values()) + [dungmoi]
    }
    df_web = pd.DataFrame(data_web)
    df_web["Thể tích (mL)"] = (df_web["Phần trăm (%)"] / 100) * volume

    df_display = df_web.copy()
    df_display["Phần trăm (%)"] = df_display["Phần trăm (%)"].map("{:.2f}".format)
    df_display["Thể tích (mL)"] = df_display["Thể tích (mL)"].map("{:.3f}".format)

    st.table(df_display)
    st.info(f"💡 Mô tả: Tỉ lệ này tạo ra hương thơm phù hợp với **{season}** (lưu ý: không tuyên bố an toàn).")

    clean_names = [limits[k]["clean"] for k in ingredients.keys()] + ["Ethanol 96%"]
    df_export = pd.DataFrame({
        "Thành phần": clean_names,
        "Phần trăm (%)": df_display["Phần trăm (%)"],
        "Thể tích (mL)": df_display["Thể tích (mL)"]
    })

    excel_html = f"""
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head><meta charset="utf-8"></head>
    <body>
        <table border="1" style="border-collapse: collapse; font-family: Arial; font-size: 12pt;">
            <colgroup>
                <col style="width: 220px;">
                <col style="width: 160px;">
                <col style="width: 160px;">
            </colgroup>
            <thead>
                <tr style="background-color: {t['primary']}; color: white; font-weight: bold; text-align: center;">
                    <th>Thành phần</th>
                    <th>Phần trăm (%)</th>
                    <th>Thể tích (mL)</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, row in df_export.iterrows():
        excel_html += f"""
                <tr>
                    <td style="padding: 8px;">{row['Thành phần']}</td>
                    <td style="padding: 8px; text-align: right;">{row['Phần trăm (%)']}</td>
                    <td style="padding: 8px; text-align: right;">{row['Thể tích (mL)']}</td>
                </tr>
        """
    excel_html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 Tải bảng Excel (Đã giãn cột & Không lỗi phông)",
            data=excel_html.encode('utf-8-sig'),
            file_name='ket_qua_pha_che.xls',
            mime='application/vnd.ms-excel',
        )
    with c2:
        df_csv = df_export.copy()
        df_csv.columns = ["Thành phần            ", "Phần trăm (%)      ", "Thể tích (mL)      "]
        csv = df_csv.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 Tải bảng kết quả (CSV)",
            data=csv,
            file_name='ket_qua_pha_che.csv',
            mime='text/csv',
        )
else:
    st.error("🚫 Trạng thái: CHƯA HỢP LỆ")

# 5. Phần 4: Trợ lý AI Gemini tư vấn nồng độ (Chat + Voice)
st.header("💬 4. Trợ lý AI Gemini tư vấn nồng độ")
st.caption("AI tự động đọc thông số thanh trượt ở trên để tư vấn. Hỗ trợ nhập bằng văn bản hoặc giọng nói.")

chat_box = st.container(height=420)
with chat_box:
    total_msgs = len(st.session_state.messages)
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("audio"):
                is_latest = idx == total_msgs - 1
                st.audio(
                    msg["audio"],
                    format="audio/mp3",
                    autoplay=(auto_play_voice and is_latest),
                )

voice_audio = st.audio_input("🎙️ Nhấn để nói với AI:")
text_prompt = st.chat_input("Nhập câu hỏi về nồng độ tinh dầu...")

pending_text = None
pending_voice = None

if voice_audio is not None:
    raw_bytes = voice_audio.getvalue()
    audio_hash = hashlib.md5(raw_bytes).hexdigest()
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        pending_voice = raw_bytes

if text_prompt:
    pending_text = text_prompt

if pending_text or pending_voice:
    if not api_key:
        st.error("Vui lòng nhập Gemini API Key ở thanh bên trái (Sidebar) để trò chuyện.")
    else:
        system_instruction = build_system_instruction(
            season, volume, ingredients, limits, dungmoi, valid
        )
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1beta"))

        if pending_voice:
            user_display = "🎙️ *[Tin nhắn thoại]*"
        else:
            user_display = pending_text

        history_snapshot = list(st.session_state.messages)

        with st.spinner("Gemini đang phân tích và tạo giọng nói..."):
            try:
                reply_text = ask_gemini(
                    client=client,
                    model_name=model_name,
                    system_instruction=system_instruction,
                    history=history_snapshot,
                    user_text=pending_text,
                    audio_bytes=pending_voice,
                )
                reply_audio = text_to_speech_bytes(reply_text)
                st.session_state.messages.append(
                    {"role": "user", "content": user_display, "audio": None}
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply_text,
                        "audio": reply_audio,
                    }
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Đã xảy ra lỗi khi gọi Gemini hoặc tạo giọng nói: {exc}")
