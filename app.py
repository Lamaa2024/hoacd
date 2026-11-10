import streamlit as st 
import pandas as pd 

st.set_page_config(page_title="Công cụ tính toán pha chế", page_icon="🧪", layout="centered")

# 1. Tạo vị trí giữ chỗ ở ĐẦU TRANG cho Cảnh báo và Tiêu đề (đúng thứ tự code gốc)
top_placeholder = st.container()

# 2. Phần 1: Thiết lập cơ bản
st.header("1. Thiết lập cơ bản")
season = st.selectbox("Chọn mùa:", ["Mùa đông", "Mùa xuân", "Mùa hạ", "Mùa thu"])
volume = st.number_input("Thể tích của mẻ (mL):", min_value=1.0, max_value=20.0, value=10.0, step=1.0)

# Bộ màu trang trí tự động thay đổi theo mùa đã chọn
themes = {
    "Mùa đông": {
        "bg": "linear-gradient(135deg, #e0f2fe 0%, #f1f5f9 100%)",
        "primary": "#0284c7",
        "secondary": "#38bdf8",
        "border": "#bae6fd"
    },
    "Mùa xuân": {
        "bg": "linear-gradient(135deg, #fce4ec 0%, #fff1f2 100%)",
        "primary": "#d81b60",
        "secondary": "#f43f5e",
        "border": "#f8bbd0"
    },
    "Mùa hạ": {
        "bg": "linear-gradient(135deg, #fef9c3 0%, #ffedd5 100%)",
        "primary": "#ea580c",
        "secondary": "#f59e0b",
        "border": "#fed7aa"
    },
    "Mùa thu": {
        "bg": "linear-gradient(135deg, #fef3c7 0%, #fae8ff 100%)",
        "primary": "#b45309",
        "secondary": "#d97706",
        "border": "#fde68a"
    }
}
t = themes[season]

# CSS trang trí xung quanh web và đổi màu theo mùa
st.markdown(f"""
<style>
    /* Nền trang web sinh động đổi màu theo mùa */
    .stApp {{
        background: {t['bg']};
    }}
    
    /* Khung chính ở giữa được bo góc và đổ bóng nổi bật */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.92);
        padding: 2.5rem 3rem !important;
        border-radius: 20px;
        border: 2px solid {t['border']};
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}

    /* Trang trí tiêu đề chính */
    h1 {{
        color: {t['primary']} !important;
        text-align: center;
        font-weight: 800 !important;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid {t['border']};
    }}

    /* Trang trí các tiêu đề mục 1, 2, 3 */
    h2 {{
        color: {t['primary']} !important;
        border-left: 5px solid {t['primary']};
        padding-left: 10px;
        margin-top: 1.5rem !important;
    }}

    /* Làm đẹp bảng hiển thị kết quả */
    table {{
        width: 100%;
        border-collapse: collapse;
        border-radius: 10px;
        overflow: hidden;
    }}
    th {{
        background-color: {t['primary']} !important;
        color: white !important;
        text-align: center !important;
        padding: 10px !important;
    }}
    td {{
        text-align: center !important;
        padding: 8px !important;
    }}

    /* Nút bấm tải xuống đổi màu theo mùa */
    .stDownloadButton > button {{
        width: 100%;
        background: linear-gradient(90deg, {t['primary']}, {t['secondary']});
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1rem;
        transition: 0.3s;
    }}
    .stDownloadButton > button:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
</style>
""", unsafe_allow_html=True)

# Hiển thị Cảnh báo và Tiêu đề ở đúng vị trí trên cùng
with top_placeholder:
    st.warning("Cần giáo viên duyệt an toàn trước khi pha:")
    st.title("Công cụ tính toán pha chế")

# 3. Phần 2: Điều chỉnh thành phần (Giữ nguyên như code gốc, bỏ icon lỗi phông)
st.header("2. Điều chỉnh thành phần")
st.write("Sử dụng thanh trượt để điều chỉnh 6 thành phần trong giới hạn.")
limits = {
    "Bưởi": {"max": 2.0, "default": 1.0},
    "Rasberry": {"max": 2.0, "default": 1.0},
    "Trà": {"max": 2.0, "default": 1.0},
    "Hoa Nhài": {"max": 2.0, "default": 1.0},
    "Amber": {"max": 2.0, "default": 1.0},
    "Sandalwood": {"max": 2.0, "default": 1.0},
    "Cedarwood": {"max": 2.0, "default": 1.0},
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
st.header("3. Kết quả & Kiểm tra")
valid = True
if dungmoi < 0:
    st.error(f"Lỗi: Dung môi bị âm ({dungmoi:.2f}%)")
    valid = False
for name, val in ingredients.items():
    if val > limits[name]["max"]:
        st.error(f"Lỗi: {name} Vượt giới hạn!")
        valid = False

if valid:
    st.success("Trạng thái: ĐƯỢC GỬI GV DUYỆT")
    data = {
        "Thành phần": list(ingredients.keys()) + ["Ethanol 96%"],
        "Phần trăm (%)": list(ingredients.values()) + [dungmoi]
    }
    df = pd.DataFrame(data)
    df["Thể tích (mL)"] = (df["Phần trăm (%)"] / 100) * volume
    
    df_display = df.copy()
    df_display["Phần trăm (%)"] = df_display["Phần trăm (%)"].map("{:.2f}".format)
    df_display["Thể tích (mL)"] = df_display["Thể tích (mL)"].map("{:.3f}".format)
    
    st.table(df_display)
    st.info("Mô tả: Tỉ lệ này tạo ra hương thơm phù hợp với mùa đã chọn (lưu ý: không tuyên bố an toàn).")
    
    # Tạo dữ liệu bảng đã giãn rộng cột sẵn (220px) để khi mở bằng Excel không bị che chữ "Thành phần"
    excel_html = f"""
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head><meta charset="utf-8"></head>
    <body>
        <table border="1" style="border-collapse: collapse; font-family: Arial; font-size: 12pt;">
            <colgroup>
                <col style="width: 200px;">
                <col style="width: 150px;">
                <col style="width: 150px;">
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
    for _, row in df_display.iterrows():
        excel_html += f"""
                <tr>
                    <td style="padding: 6px;">{row['Thành phần']}</td>
                    <td style="padding: 6px; text-align: right;">{row['Phần trăm (%)']}</td>
                    <td style="padding: 6px; text-align: right;">{row['Thể tích (mL)']}</td>
                </tr>
        """
    excel_html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Chia 2 nút tải: 1 nút tải file đã giãn cột sẵn cho Excel, 1 nút CSV gốc
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 Tải bảng kết quả (Đã giãn cột Excel)",
            data=excel_html.encode('utf-8-sig'),
            file_name='ket_qua_pha_che.xls',
            mime='application/vnd.ms-excel',
        )
    with c2:
        # Thêm khoảng trắng đệm vào CSV để cột rộng hơn một chút khi mở trực tiếp
        df_csv = df_display.copy()
        df_csv.columns = ["Thành phần          ", "Phần trăm (%)     ", "Thể tích (mL)     "]
        csv = df_csv.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 Tải bảng kết quả (CSV)",
            data=csv,
            file_name='ket_qua_pha_che.csv',
            mime='text/csv',
        )
else: 
    st.error("Trạng thái: CHƯA HỢP LỆ")
