import streamlit as st
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(
    page_title="Perfume Lab - Công cụ pha chế",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Thanh bên (Sidebar) trang trí xung quanh web cho sinh động
with st.sidebar:
    st.markdown("## 🌸 Perfume Studio")
    st.caption("Hệ thống hỗ trợ pha chế & kiểm soát định lượng hương liệu chuẩn phòng Lab.")
    st.divider()
    
    st.markdown("### 🧪 Quy tắc pha chế")
    st.info(
        "1. **Tầng hương đầu:** Bưởi, Raspberry\n"
        "2. **Tầng hương giữa:** Trà, Hoa Nhài\n"
        "3. **Tầng hương cuối:** Amber, Sandalwood, Cedarwood"
    )
    
    st.markdown("### 📋 Hướng dẫn")
    st.markdown("""
    - **Bước 1:** Chọn mùa để đổi giao diện và định hướng mùi hương.
    - **Bước 2:** Nhập thể tích mẻ pha chế.
    - **Bước 3:** Kéo thanh trượt điều chỉnh tỉ lệ.
    - **Bước 4:** Tải file bảng tính đã được căn chỉnh sẵn độ rộng cột.
    """)
    st.divider()
    if st.button("🎉 Bắn pháo hoa ăn mừng", use_container_width=True):
        st.balloons()

# 3. Khởi tạo bộ màu sắc động theo từng mùa
season_themes = {
    "🌸 Mùa xuân": {
        "bg": "linear-gradient(135deg, #fff5f7 0%, #fce4ec 100%)",
        "primary": "#d81b60",
        "secondary": "#ff80ab",
        "card_border": "#f8bbd0",
        "badge": "🌸 Hương Xuân: Tươi mới, ngọt ngào & lãng mạn"
    },
    "☀️ Mùa hạ": {
        "bg": "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)",
        "primary": "#0284c7",
        "secondary": "#38bdf8",
        "card_border": "#bae6fd",
        "badge": "☀️ Hương Hạ: Thanh mát, sảng khoái & tràn đầy năng lượng"
    },
    "🍂 Mùa thu": {
        "bg": "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
        "primary": "#d97706",
        "secondary": "#fbbf24",
        "card_border": "#fde68a",
        "badge": "🍂 Hương Thu: Ấm áp, dịu dàng & sâu lắng"
    },
    "❄️ Mùa đông": {
        "bg": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
        "primary": "#334155",
        "secondary": "#64748b",
        "card_border": "#cbd5e1",
        "badge": "❄️ Hương Đông: Trầm ấm, sang trọng & bí ẩn"
    }
}

# 4. Bố cục chọn mùa trước để lấy màu chủ đạo
col_left, col_right = st.columns([1.25, 1], gap="large")

with col_left:
    with st.container(border=True):
        st.subheader("🛠️ 1. Thiết lập cơ bản")
        c1, c2 = st.columns(2)
        with c1:
            season = st.selectbox(
                "Chọn mùa chủ đạo (Đổi màu giao diện):", 
                list(season_themes.keys())
            )
        with c2:
            volume = st.number_input(
                "Thể tích của mẻ (mL):", 
                min_value=1.0, max_value=20.0, value=10.0, step=1.0
            )

# Lấy bảng màu tương ứng với mùa đang chọn
theme = season_themes[season]

# 5. Áp dụng CSS trang trí xung quanh web theo màu của mùa
st.markdown(f"""
<style>
    /* Nền trang đổi màu theo mùa */
    .stApp {{
        background: {theme['bg']};
    }}
    
    /* Khung tiêu đề Banner rực rỡ */
    .hero-banner {{
        background: linear-gradient(120deg, {theme['primary']}, {theme['secondary']});
        padding: 1.5rem 2rem;
        border-radius: 18px;
        color: white;
        text-align: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }}
    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        opacity: 0.95;
        margin-top: 0.4rem;
    }}

    /* Trang trí các thẻ khung trắng (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 16px !important;
        border: 2px solid {theme['card_border']} !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
        padding: 1.2rem;
        transition: transform 0.2s ease;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-2px);
    }}

    /* Nút bấm tải xuống đổi màu theo mùa */
    .stDownloadButton > button {{
        width: 100%;
        background: linear-gradient(90deg, {theme['primary']}, {theme['secondary']});
        color: white !important;
        font-weight: 700;
        font-size: 1rem;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }}
    .stDownloadButton > button:hover {{
        transform: scale(1.02);
        filter: brightness(1.08);
    }}
</style>
""", unsafe_allow_html=True)

# Hiển thị Banner trên cùng (Dùng container đầu trang)
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">✨ CÔNG CỤ TÍNH TOÁN PHA CHẾ ✨</div>
    <div class="hero-subtitle">{theme['badge']}</div>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ **Cần giáo viên duyệt an toàn trước khi pha:** Kiểm tra kỹ định lượng trước khi thực hành!")

# 6. Tiếp tục phần điều chỉnh thành phần ở cột bên trái
limits = {
    "Bưởi": {"icon": "🍊", "max": 2.0, "default": 1.0},
    "Raspberry": {"icon": "🍓", "max": 2.0, "default": 1.0},
    "Trà": {"icon": "🍵", "max": 2.0, "default": 1.0},
    "Hoa Nhài": {"icon": "🌼", "max": 2.0, "default": 1.0},
    "Amber": {"icon": "✨", "max": 2.0, "default": 1.0},
    "Sandalwood": {"icon": "🪵", "max": 2.0, "default": 1.0},
    "Cedarwood": {"icon": "🌲", "max": 2.0, "default": 1.0},
}

ingredients = {}
with col_left:
    with st.container(border=True):
        st.subheader("🌿 2. Điều chỉnh thành phần")
        st.caption("Sử dụng thanh trượt để điều chỉnh 7 thành phần hương liệu trong giới hạn.")
        
        slider_cols = st.columns(2)
        for idx, (name, config) in enumerate(limits.items()):
            with slider_cols[idx % 2]:
                ingredients[name] = st.slider(
                    f"{config['icon']} {name} (≤ {config['max']}%)", 
                    min_value=0.0, 
                    max_value=config['max'], 
                    value=config["default"], 
                    step=0.1
                )

# 7. Tính toán kết quả
total = sum(ingredients.values())
dungmoi = 100.0 - total

# Hàm tạo file Excel (.xls) có định sẵn độ rộng cột để KHÔNG BỊ CHE CHỮ & KHÔNG LỖI FONT
def generate_auto_width_excel(df_clean):
    html_table = f"""
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head>
        <meta charset="utf-8">
        <style>
            table {{ border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12pt; }}
            th {{ background-color: {theme['primary']}; color: white; font-weight: bold; padding: 10px; border: 1px solid #999; text-align: center; }}
            td {{ padding: 8px 12px; border: 1px solid #ccc; }}
            .num {{ text-align: right; mso-number-format:"0\\.00"; }}
            .vol {{ text-align: right; mso-number-format:"0\\.000"; }}
        </style>
    </head>
    <body>
        <table>
            <colgroup>
                <col style="width: 220px;">
                <col style="width: 160px;">
                <col style="width: 160px;">
            </colgroup>
            <thead>
                <tr>
                    <th>Thành phần</th>
                    <th>Phần trăm (%)</th>
                    <th>Thể tích (mL)</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, row in df_clean.iterrows():
        html_table += f"""
                <tr>
                    <td>{row['Thành phần']}</td>
                    <td class="num">{row['Phần trăm (%)']:.2f}</td>
                    <td class="vol">{row['Thể tích (mL)']:.3f}</td>
                </tr>
        """
    html_table += """
            </tbody>
        </table>
    </body>
    </html>
    """
    return html_table.encode('utf-8-sig')

# 8. Hiển thị kết quả ở cột bên phải
with col_right:
    with st.container(border=True):
        st.subheader("📊 3. Kết quả & Kiểm tra")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🌸 Tinh dầu", f"{total:.1f}%")
        m2.metric("💧 Dung môi", f"{dungmoi:.1f}%")
        m3.metric("🧪 Thể tích mẻ", f"{volume:.1f} mL")
        
        st.divider()
        
        valid = True
        if dungmoi < 0:
            st.error(f"❌ Lỗi: Dung môi bị âm ({dungmoi:.2f}%)")
            valid = False
        for name, val in ingredients.items():
            if val > limits[name]["max"]:
                st.error(f"❌ Lỗi: {name} vượt giới hạn!")
                valid = False
                
        if valid:
            st.success("✅ **Trạng thái: ĐƯỢC GỬI GV DUYỆT**")
            
            # Bảng 1: Dùng để hiển thị trên Web (Có icon đẹp mắt)
            web_names = [f"{limits[k]['icon']} {k}" for k in ingredients.keys()] + ["💧 Ethanol 96%"]
            df_web = pd.DataFrame({
                "Thành phần": web_names,
                "Phần trăm (%)": list(ingredients.values()) + [dungmoi]
            })
            df_web["Thể tích (mL)"] = (df_web["Phần trăm (%)"] / 100) * volume
            
            st.dataframe(
                df_web,
                column_config={
                    "Thành phần": st.column_config.TextColumn("Thành phần hương", width="medium"),
                    "Phần trăm (%)": st.column_config.ProgressColumn(
                        "Phần trăm (%)", format="%.2f%%", min_value=0, max_value=100
                    ),
                    "Thể tích (mL)": st.column_config.NumberColumn("Thể tích (mL)", format="%.3f mL")
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info(f"💡 **Mô tả:** Tỉ lệ này tạo ra hương thơm phù hợp với **{season}** (lưu ý: không tuyên bố an toàn).")
            
            # Bảng 2: Dùng để xuất file (Đã bỏ icon gây lỗi phông chữ trong Excel)
            clean_names = list(ingredients.keys()) + ["Ethanol 96%"]
            df_clean = pd.DataFrame({
                "Thành phần": clean_names,
                "Phần trăm (%)": list(ingredients.values()) + [dungmoi],
                "Thể tích (mL)": [(v / 100) * volume for v in (list(ingredients.values()) + [dungmoi])]
            })
            
            # Nút 1: Tải file Excel (.xls) ĐÃ GIÃN RỘNG CỘT SẴN & TÔ MÀU ĐẸP
            excel_data = generate_auto_width_excel(df_clean)
            st.download_button(
                label="📥 Tải bảng Excel (Đã giãn rộng cột & Không lỗi phông)",
                data=excel_data,
                file_name='ket_qua_pha_che.xls',
                mime='application/vnd.ms-excel',
            )
            
            # Nút 2: Tải file CSV chuẩn (Đã xóa icon lỗi phông và thêm khoảng trắng tiêu đề)
            df_csv = df_clean.copy()
            df_csv["Phần trăm (%)"] = df_csv["Phần trăm (%)"].map("{:.2f}".format)
            df_csv["Thể tích (mL)"] = df_csv["Thể tích (mL)"].map("{:.3f}".format)
            csv_data = df_csv.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📄 Tải file CSV thuần (Không lỗi phông)",
                data=csv_data,
                file_name='ket_qua_pha_che.csv',
                mime='text/csv',
            )
        else: 
            st.error("🚫 **Trạng thái: CHƯA HỢP LỆ**")
