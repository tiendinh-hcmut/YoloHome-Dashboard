from machine import Pin, SoftI2C
from homebit3_dht20 import DHT20
from yolobit import *
from aiot_lcd1602 import LCD1602
import time
import sys
import uselect

button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1

# =========================
# I2C
# =========================
i2c = SoftI2C(scl=Pin(20), sda=Pin(19))
dht20 = DHT20()

# =========================
# LCD
# =========================
lcd = LCD1602()
lcd.clear()
lcd.putstr("System Ready")

# =========================
# PUMP CONTROL
# Dung pin13 analog muc 10%
# =========================
PUMP_PERCENT_ON = 15
PUMP_TIMEOUT_MS = 120000

pump_on = False
last_pump_command_time = 0

def set_pump_state(is_on):
    global pump_on
    pump_on = is_on

    if is_on:
        pin13.write_analog(round(translate(PUMP_PERCENT_ON, 0, 100, 0, 1023)))
    else:
        pin13.write_analog(round(translate(0, 0, 100, 0, 1023)))

def pump_status_text():
    return "1" if pump_on else "0"

def update_lcd_pump(on_state):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("PUMP STATUS")
    lcd.move_to(0, 1)
    lcd.putstr("PUMP ON" if on_state else "PUMP OFF")

# Tắt pump lúc khởi động
set_pump_state(False)
update_lcd_pump(False)

last_read_time = 0
cmd_buffer = ""

spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

while True:
    current_time = time.ticks_ms()

    # ==========================================
    # NHẬN LỆNH TỪ GATEWAY
    # ==========================================
    if spoll.poll(0):
        try:
            char = sys.stdin.read(1)

            if char:
                cmd_buffer += char

                while "!" in cmd_buffer and "#" in cmd_buffer:
                    start = cmd_buffer.find("!")
                    end = cmd_buffer.find("#")

                    if start < end:
                        msg = cmd_buffer[start:end]
                        msg = msg.replace("!", "")
                        parts = msg.split(":")

                        if len(parts) >= 2:
                            # !ACTION:1# hoặc !ACTION:0#
                            if parts[0] == "ACTION":
                                command = parts[1]

                                if command == "1" or command == "ON":
                                    lcd.clear()
                                    lcd.move_to(0, 0)
                                    lcd.puts("TRANG THAI:")
                                    lcd.move_to(0, 1)
                                    lcd.putstr("NONG")
                                    print("!DEBUG:MAN HINH HIEN THI NONG#")

                                elif command == "0" or command == "OFF":
                                    lcd.clear()
                                    lcd.putstr("Nhiet do OK")
                                    print("!DEBUG:MAN HINH DA XOA#")

                            # !LCD:...#
                            elif parts[0] == "LCD":
                                lcd.clear()
                                lcd.puts(parts[1])
                                print("!DEBUG:CAP NHAT LCD TU DASHBOARD#")

                            # !PUMP:1# hoặc !PUMP:0#
                            elif parts[0] == "PUMP":
                                command = parts[1]
                                last_pump_command_time = current_time

                                if command == "1" or command == "ON":
                                    set_pump_state(True)
                                    update_lcd_pump(True)
                                    print("!DEBUG:PUMP DA BAT#")
                                    print("!STATUS:PUMP:1#")

                                elif command == "0" or command == "OFF":
                                    set_pump_state(False)
                                    update_lcd_pump(False)
                                    print("!DEBUG:PUMP DA TAT#")
                                    print("!STATUS:PUMP:0#")

                    cmd_buffer = cmd_buffer[end + 1:]

        except Exception:
            pass

    # ==========================================
    # TỰ TẮT SAU 10 GIÂY KHÔNG CÓ LỆNH MỚI
    # ==========================================
    if pump_on:
        if time.ticks_diff(current_time, last_pump_command_time) >= PUMP_TIMEOUT_MS:
            set_pump_state(False)
            update_lcd_pump(False)
            print("!DEBUG:PUMP TU DONG TAT DO TIMEOUT 10S#")
            print("!STATUS:PUMP:0#")
            last_pump_command_time = current_time

    # ==========================================
    # GỬI SENSOR ĐỊNH KỲ
    # ==========================================
    if time.ticks_diff(current_time, last_read_time) >= 10000:
        try:
            temp = dht20.dht20_temperature()
            humi = dht20.dht20_humidity()

            light_raw = pin1.read_analog()
            light_percent = round((light_raw / 4095) * 100)

            print("!SENSORS:TEMP:{}#".format(temp))
            print("!SENSORS:HUMI:{}#".format(humi))
            print("!SENSORS:LIGHT:{}#".format(light_percent))
            print("!STATUS:PUMP:{}#".format(pump_status_text()))

        except Exception:
            print("!DEBUG:LOI DOC CAM BIEN#")

        last_read_time = current_time

    time.sleep_ms(50)