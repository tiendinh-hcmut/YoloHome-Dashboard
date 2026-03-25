import serial.tools.list_ports
import time
import sys
from Adafruit_IO import MQTTClient

# Thông tin tài khoản Adafruit IO (Nên reset lại Key sau khi demo xong nhé)
AIO_USERNAME = "tiendinh2110"
AIO_KEY = "dan_key_vao_day"

FEED_TEMP = "bbc-temp"
FEED_LCD = "bbc-lcd"

def connected(client):
    print("✅ Ket noi server Adafruit IO thanh cong!")
    client.subscribe(FEED_LCD)

def subscribe(client, userdata, mid, granted_qos):
    print("📡 Dang lang nghe lenh tu Web...")

def disconnected(client):
    print("❌ Ngat ket noi voi server...")
    sys.exit(1)

def message(client, feed_id, payload):
    print(f"\n[SERVER -> MẠCH] Nhan du lieu tu '{feed_id}': {payload}")
    if feed_id == FEED_LCD:
        # THÊM \n VÀO ĐUÔI ĐỂ ÉP USB XẢ DỮ LIỆU XUỐNG MẠCH NGAY LẬP TỨC
        uart_msg = f"!LCD:{payload}#\n"
        ser.write(uart_msg.encode('utf-8'))
        print(f"👉 Da truyen lenh xuong Yolo:Bit: {uart_msg.strip()}")

try:
    ser = serial.Serial(port="COM5", baudrate=115200)
    print("🔌 Mo cong Serial COM5 thanh cong!")
except Exception as e:
    print(f"⚠️ Loi mo cong Serial: {e}")
    sys.exit(1)

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

mess = "" 

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    
    if len(splitData) > 1:
        if splitData[1] == "TEMP":
            nhiet_do = splitData[2]
            client.publish(FEED_TEMP, nhiet_do)
            print(f"[MẠCH -> SERVER] Da cap nhat nhiet do: {nhiet_do} °C")
        # THÊM LUỒNG NÀY ĐỂ NGHE YOLO:BIT PHẢN HỒI LẠI
        elif splitData[0] == "DEBUG": 
            print(f"🛠️ [YOLOBIT BÁO CÁO]: {splitData[1]}")

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8", errors='ignore')
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start : end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end + 1:]

print("\n🚀 GATEWAY ĐANG HOẠT ĐỘNG (Nhấn Ctrl+C để tắt)\n" + "-"*40)
while True:
    try:
        readSerial()
        time.sleep(0.1) 
    except KeyboardInterrupt:
        print("\n🛑 Da tat Gateway an toan.")
        ser.close()
        sys.exit(0)