import streamlit as st
from Adafruit_IO import Client, RequestError
import time

# --- ADAFRUIT IO CONFIGURATION ---
ADAFRUIT_AIO_USERNAME = st.secrets["AIO_USERNAME"]
ADAFRUIT_AIO_KEY      = st.secrets["AIO_KEY"]

# Initialize connection
aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

# --- WEB UI DESIGN ---
st.set_page_config(page_title="YoloHome Control Panel", layout="centered")
st.title("🏡 YoloHome System")

# --- SECTION 1: Environment Monitoring (Receive Data) ---
st.header("Environment Monitoring")

try:
    # Fetch the latest data from the 'bbc-temp' feed
    data_nhiet_do = aio.receive('bbc-temp')
    
    # Display the metric
    st.metric(label="Current Temperature", value=f"{data_nhiet_do.value} °C")

except RequestError as e:
    st.error(f"Connection error: {e}")

st.divider() # Add a dividing line

# --- SECTION 2: Message Control (Send Data to LCD) ---
st.header("Send Message to Home")
st.caption("Enter text to display on the physical LCD screen (Max 16 chars).")

# Use a form to group input and button for cleaner refresh handling
with st.form(key='lcd_message_form', clear_on_submit=True):
    # Text input field
    user_message = st.text_input(label="Enter Message:", max_chars=16, placeholder="Hello World")
    
    # Submit button
    submit_button = st.form_submit_button(label='Send to LCD')

    if submit_button:
        if user_message:
            try:
                # SEND THE DATA to the 'bbc-lcd' feed
                aio.send_data('bbc-lcd', user_message)
                st.success(f"Message '{user_message}' successfully sent!")
                
                # Brief pause so user can see the success message before auto-refresh
                time.sleep(1) 
            except RequestError as e:
                st.error(f"Failed to send message: {e}")
        else:
            st.warning("Please enter a message first.")

st.divider() # Add another dividing line

# Information Caption
st.caption(f"Status: Live Update Every 10s. Last contact: {time.strftime('%H:%M:%S')}")

# --- AUTO UPDATE MECHANISM (Receive Side Only) ---
# Pause for 10 seconds (Increase slightly to allow sending time)
time.sleep(10)
# Rerun the script to fetch new temperature data
st.rerun()
