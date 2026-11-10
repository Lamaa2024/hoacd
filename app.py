import streamlit as st 
import pandas as pd 

# 1. Cấu hình trang (Phải đặt ở dòng đầu tiên của lệnh Streamlit)
st.set_page_config(
    page_title="Perfume Lab - Công cụ pha chế",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Trang trí bằng Custom CSS
st.markdown("""
<style>
    /* Nền trang nhẹ nhàng, sang trọng */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* Tiêu đề chính */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #2b5876, #4e4376);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        text-align: center;
        color: #6c757d;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }

    /* Đổ bóng cho các khung chứa (container) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        border: 1px solid #f0f0f0 !important;
        padding: 1rem;
    }

    /* Tùy chỉnh nút Tải xuống */
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(45deg, #2b5876, #4e4376);
        color: white !important;
        font-weight: 600;
        border-radius: 10px;
        border: none;
        padding: 0.65rem 1rem;
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(78, 67, 118, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 3. Header & Cảnh báo
st.markdown('<div class="main-title">🧪 CÔNG CỤ TÍNH TOÁN PHA CHẾ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Hệ thống thiết kế công thức hương thơm & kiểm soát định lượng an toàn</div>', unsafe_allow_html=True)

st.warning("⚠️ **Lưu ý an toàn:** Cần giáo viên duyệt công thức trước khi tiến hành pha chế thực tế!")

# 4. Bố cục chia 2 cột chính
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    with st.container(border=True):
        st.subheader("🛠️ 1. Thiết lập cơ bản")
        c1, c2 = st.columns(2)
        with c1:
            season = st.selectbox(
                "Chọn mùa chủ đạo:", 
                ["❄️ Mùa đông", "🌸 Mùa xuân", "☀️ Mùa hạ", "🍂 Mùa thu"]
            )
        with c2:
            volume = st.number_input(
                "Thể tích của mẻ (mL):", 
                min_value=1.0, max_value=20.0, value=10.0, step=1.0
            )

    with st.container(border=True):
        st.subheader("🌿 2. Điều chỉnh thành phần")
        st.caption("Sử dụng thanh trượt để điều chỉnh các nốt hương trong giới hạn cho phép.")
        
        limits = {
            "🍊 Bưởi": {"max": 2.0, "default": 1.0},
            "🍓 Raspberry": {"max": 2.0, "default": 1.0},
            "🍵 Trà": {"max": 2.0, "default": 1.0},
            "🌼 Hoa Nhài": {"max": 2.0, "default": 1.0},
            "✨ Amber": {"max": 2.0, "default": 1.0},
            "🪵 Sandalwood": {"max": 2.0, "default": 1.0},
            "🌲 Cedarwood": {"max": 2.0, "default": 1.0},
        }
        
        ingredients = {}
        # Chia 2 cột cho các thanh trượt đỡ bị dài trang
        slider_cols = st.columns(2)
        for idx, (name, config) in enumerate(limits.items()):
            with slider_cols[idx % 2]:
                ingredients[name] = st.slider(
                    f"{name} (≤ {config['max']}%)", 
                    min_value=0.0, 
                    max_value=config['max'], 
                    value=config["default"], 
                    step=0.1
                )

# 5. Tính toán dữ liệu
total = sum(ingredients.values())
dungmoi = 100.0 - total

# 6. Cột bên phải: Hiển thị kết quả & Dashboard
with col_right:
    with st.container(border=True):
        st.subheader("📊 3. Kết quả & Kiểm tra")
        
        # Thẻ hiển thị chỉ số nhanh (Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng tinh dầu", f"{total:.1f}%")
        m2.metric("Ethanol 96%", f"{dungmoi:.1f}%")
        m3.metric("Tổng thể tích", f"{volume:.1f} mL")
        
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
            
            # Tạo bảng dữ liệu
            data = {
                "Thành phần": list(ingredients.keys()) + ["💧 Ethanol 96% (Dung môi)"],
                "Phần trăm (%)": list(ingredients.values()) + [dungmoi]
            }
            df = pd.DataFrame(data)
            df["Thể tích (mL)"] = (df["Phần trăm (%)"] / 100) * volume
            
            # Hiển thị bảng đẹp hơn với thanh Progress bar nội bộ của Streamlit
            st.dataframe(
                df,
                column_config={
                    "Thành phần": st.column_config.TextColumn("Thành phần hương"),
                    "Phần trăm (%)": st.column_config.ProgressColumn(
                        "Tỉ lệ (%)",
                        format="%.2f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Thể tích (mL)": st.column_config.NumberColumn(
                        "Thể tích (mL)",
                        format="%.3f mL"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info(f"💡 **Mô tả:** Tỉ lệ này tạo ra hương thơm phù hợp với **{season}** (Lưu ý: Không tuyên bố an toàn).")
            
            # Chuẩn bị file CSV chuẩn để tải về (loại bỏ icon để file Excel sạch đẹp)
            df_export = df.copy()
            df_export["Phần trăm (%)"] = df_export["Phần trăm (%)"].map("{:.2f}".format)
            df_export["Thể tích (mL)"] = df_export["Thể tích (mL)"].map("{:.3f}".format)
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 Tải bảng kết quả (CSV)",
                data=csv,
                file_name='ket_qua_pha_che.csv',
                mime='text/csv',
            )
        else: 
            st.error("🚫 **Trạng thái: CHƯA HỢP LỆ**")
