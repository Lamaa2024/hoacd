import streamlit as st 
import pandas as pd 

st.set_page_config(page_title="Công cụ tính toán pha chế", page_icon="🧪", layout="centered")

# 1. Giữ chỗ ở ĐẦU TRANG cho Cảnh báo và Tiêu đề (đúng vị trí code gốc)
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

# CSS trang trí nền, khung viền và dải emoji hai bên lề trang web
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
        background-color: rgba(255, 255, 255, 0.94);
        padding: 2.5rem 3rem !important;
        border-radius: 24px;
        border: 3px solid {t['border']};
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }}

    /* Khung tiêu đề chính */
    .title-box {{
        background: linear-gradient(90deg, {t['primary']}, {t['secondary']});
        color: white;
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.12);
        margin-bottom: 1rem;
    }}

    /* Trang trí các tiêu đề mục 1, 2, 3 */
    h2 {{
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
    }}
    th {{
        background-color: {t['primary']} !important;
        color: white !important;
        text-align: center !important;
        padding: 10px !important;
        font-size: 1.05rem;
    }}
    td {{
        text-align: center !important;
        padding: 8px !important;
        font-weight: 500;
    }}

    /* Nút bấm tải xuống đổi màu theo mùa */
    .stDownloadButton > button {{
        width: 100%;
        background: linear-gradient(90deg, {t['primary']}, {t['secondary']});
        color: white !important;
        font-weight: bold;
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

# Đưa Cảnh báo và Tiêu đề lên đúng vị trí ĐẦU TRANG như code gốc
with top_placeholder:
    st.warning("⚠️ Cần giáo viên duyệt an toàn trước khi pha:")
    st.markdown('<div class="title-box">🧪✨ Công cụ tính toán pha chế ✨🌸</div>', unsafe_allow_html=True)

# 3. Phần 2: Điều chỉnh thành phần (Đầy đủ emoji trái cây, hoa lá)
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
    
    # Bảng hiển thị trên Web (Có đầy đủ emoji trái cây, hoa lá đẹp mắt)
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
    
    # Bảng dùng để xuất file (Lấy tên sạch không chứa icon để không bị lỗi ô vuông [?] trong Excel)
    clean_names = [limits[k]["clean"] for k in ingredients.keys()] + ["Ethanol 96%"]
    df_export = pd.DataFrame({
        "Thành phần": clean_names,
        "Phần trăm (%)": df_display["Phần trăm (%)"],
        "Thể tích (mL)": df_display["Thể tích (mL)"]
    })

    # Tạo bảng Excel đã cài sẵn độ rộng cột (220px) để chữ "Thành phần" hiển thị đầy đủ
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
        # Đệm thêm khoảng trắng vào tiêu đề CSV để cột rộng hơn
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
