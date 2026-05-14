import time
import sys
import serial
from serial import SerialException
from Adafruit_IO import MQTTClient

AIO_USERNAME = "thinh250305"
AIO_KEY = ""

FEED_TEMP = "bbc-temp"
FEED_HUMI = "bbc-humidity"
FEED_LIGHT = "bbc-brightness"

FEED_LCD = "bbc-lcd"
FEED_ACTION = "bbc-led"
FEED_PUMP_COMMAND = "pump-command"
FEED_PUMP_STATUS = "pump-status"

SERIAL_PORT = "COM5"
BAUD_RATE = 115200


def open_serial():
    while True:
        try:
            s = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"🔌 Mo cong Serial {SERIAL_PORT} thanh cong!")
            return s
        except Exception as e:
            print(f"⚠️ Chua mo duoc {SERIAL_PORT}: {e}")
            print("⏳ Thu lai sau 2 giay...")
            time.sleep(2)


def connected(client):
    print("✅ Ket noi server Adafruit IO thanh cong!")
    client.subscribe(FEED_LCD)
    client.subscribe(FEED_ACTION)
    client.subscribe(FEED_PUMP_COMMAND)


def subscribe(client, userdata, mid, granted_qos):
    print("📡 Dang lang nghe lenh tu Adafruit IO...")


def disconnected(client):
    print("❌ Ngat ket noi voi server...")
    sys.exit(1)


def send_uart_message(message_text):
    global ser
    uart_msg = message_text + "\n"
    try:
        ser.write(uart_msg.encode("utf-8"))
        print(f"👉 Da truyen xuong mach: {message_text}")
    except SerialException as e:
        print(f"⚠️ Loi ghi serial: {e}")


def message(client, feed_id, payload):
    print(f"\n[SERVER -> MACH] Nhan du lieu tu '{feed_id}': {payload}")

    if feed_id == FEED_LCD:
        send_uart_message(f"!LCD:{payload}#")

    elif feed_id == FEED_ACTION:
        send_uart_message(f"!ACTION:{payload}#")

    elif feed_id == FEED_PUMP_COMMAND:
        send_uart_message(f"!PUMP:{payload}#")


def process_data(data):
    data = data.replace("!", "").replace("#", "")
    parts = data.split(":")

    if not parts:
        return

    if len(parts) >= 3 and parts[0] == "SENSORS":
        sensor_type = parts[1]
        sensor_value = parts[2]

        if sensor_type == "TEMP":
            client.publish(FEED_TEMP, sensor_value)
            print(f"[MACH -> SERVER] Nhiet do: {sensor_value} °C")

        elif sensor_type == "HUMI":
            client.publish(FEED_HUMI, sensor_value)
            print(f"[MACH -> SERVER] Do am: {sensor_value} %")

        elif sensor_type == "LIGHT":
            client.publish(FEED_LIGHT, sensor_value)
            print(f"[MACH -> SERVER] Anh sang: {sensor_value} %")

    elif len(parts) >= 3 and parts[0] == "STATUS":
        status_type = parts[1]
        status_value = parts[2]

        if status_type == "PUMP":
            client.publish(FEED_PUMP_STATUS, status_value)
            print(f"[MACH -> SERVER] Pump status: {status_value}")

    elif len(parts) >= 2 and parts[0] == "DEBUG":
        debug_msg = ":".join(parts[1:])
        print(f"🛠️ [YOLOBIT BAO CAO]: {debug_msg}")


def read_serial():
    global serial_buffer, ser

    try:
        bytes_to_read = ser.in_waiting
        if bytes_to_read > 0:
            serial_buffer += ser.read(bytes_to_read).decode("utf-8", errors="ignore")

            while ("!" in serial_buffer) and ("#" in serial_buffer):
                start = serial_buffer.find("!")
                end = serial_buffer.find("#")

                if start < end:
                    packet = serial_buffer[start:end + 1]
                    process_data(packet)

                if end == len(serial_buffer) - 1:
                    serial_buffer = ""
                else:
                    serial_buffer = serial_buffer[end + 1:]

    except SerialException as e:
        print(f"⚠️ Mat ket noi serial: {e}")
        try:
            ser.close()
        except Exception:
            pass

        print("🔄 Dang mo lai cong serial...")
        time.sleep(2)
        ser = open_serial()


ser = open_serial()

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()

serial_buffer = ""

print("\n🚀 GATEWAY DANG HOAT DONG (Nhan Ctrl+C de tat)\n" + "-" * 40)

while True:
    try:
        read_serial()
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Da tat Gateway an toan.")
        try:
            ser.close()
        except Exception:
            pass
        sys.exit(0)