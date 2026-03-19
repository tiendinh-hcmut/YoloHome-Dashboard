import streamlit as st
from Adafruit_IO import Client, RequestError

# --- CẤU HÌNH ADAFRUIT IO ---
# Thay vì ghi trực tiếp chữ, ta dùng hàm st.secrets để giấu đi
ADAFRUIT_AIO_USERNAME = st.secrets["AIO_USERNAME"]
ADAFRUIT_AIO_KEY      = st.secrets["AIO_KEY"]

# Khởi tạo kết nối
aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

# --- XÂY DỰNG GIAO DIỆN WEB ---
st.set_page_config(page_title="YoloHome Dashboard", layout="centered")
st.title("🏡 Hệ thống YoloHome")
st.subheader("Giám sát Môi trường Không khí")

try:
    # Kéo dữ liệu mới nhất từ Feed có tên là 'bbc-temp'
    data_nhiet_do = aio.receive('bbc-temp')
    
    # Hiển thị thẳng số liệu ra màn hình (Không cần col1 nữa)
    st.metric(label="Nhiệt độ hiện tại", value=f"{data_nhiet_do.value} °C")

except RequestError as e:
    st.error(f"Lỗi kết nối hoặc không tìm thấy Feed: {e}")
    st.info("Hãy kiểm tra lại tên Username, Key và Tên Feed nhé.")

st.caption("Dữ liệu được cập nhật trực tiếp từ Adafruit IO.")
