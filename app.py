import streamlit as st
from Adafruit_IO import Client, RequestError
import time

# --- ADAFRUIT IO CONFIGURATION ---
ADAFRUIT_AIO_USERNAME = st.secrets["AIO_USERNAME"]
ADAFRUIT_AIO_KEY      = st.secrets["AIO_KEY"]

# Initialize connection
aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

# --- WEB UI DESIGN ---
st.set_page_config(page_title="YoloHome Dashboard", layout="centered")
st.title("🏡 YoloHome System")
st.subheader("Environment Monitoring")

try:
    # Fetch the latest data from the 'bbc-temp' feed
    data_nhiet_do = aio.receive('bbc-temp')
    
    # Display the metric directly
    st.metric(label="Current Temperature", value=f"{data_nhiet_do.value} °C")

except RequestError as e:
    st.error(f"Connection error or Feed not found: {e}")
    st.info("Please double-check your Username, Key, and Feed Name.")

st.caption(f"Data is updated in real-time from Adafruit IO. Last update: {time.strftime('%H:%M:%S')}")

# --- AUTO UPDATE MECHANISM ---
# Pause for 5 seconds
time.sleep(5)
# Rerun the script to fetch new data
st.rerun()
