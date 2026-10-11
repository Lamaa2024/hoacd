import streamlit as st 
import pandas as pd 

st.warning("Cần giáo viên duyệt an toàn trước khi pha:")
st.title("Công cụ tính toán pha chế")

st.header("1.  Thiết lập cơ bản")
season = st.selectbox("Chọn mùa:", ["Mùa đông", "Mùa xuân", "Mùa hạ", "Mùa thu"])
volume = st.number_input("Thể tích của mẻ (mL):", min_value=1.0, max_value=20.0, value=10.0, step=1.0)
st.header("2. Điều chỉnh thành phần")
st.write("Sử dụng thanh trượt để điều chỉnh 6 thành phần trong giới hạn.")
limits = {
    "Bưởi": {"max":4.0, "default":2.0},
    "Rasberry:": {"max": 4.0, "default": 2.0},
    "Trà": {"max": 3.0, "default": 1.},
    "Hoa Nhài": {"max": 3.0, "default": 1.5},
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
    data = {"Thành phần": list(ingredients.keys()) + ["Ethanol 96%"],
            "Phần trăm (%)": list(ingredients.values()) + [dungmoi]}
    df = pd.DataFrame(data)
    df["Thể tích (mL)"] = (df["Phần trăm (%)"] / 100) * volume
    df_display = df.copy()
    df_display["Phần trăm (%)"] = df_display["Phần trăm (%)"].map("{:.2f}".format)
    df_display["Thể tích (mL)"] = df_display["Thể tích (mL)"].map("{:.3f}".format)
    st.table(df_display)
    st.info("Mô tả: Tỉ lệ này tạo ra hương thơm phù hợp với mùa đã chọn (lưu ý: không tuyên bố an toàn).")
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Tải bảng kết quả (CSV)",
        data=csv,
        file_name='ket_qua_pha_che.csv',
        mime='text/csv',
    )
else: 
    st.error("Trạng thái: CHƯA HỢP LỆ")