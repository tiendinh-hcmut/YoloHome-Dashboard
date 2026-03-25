from machine import Pin, SoftI2C
from homebit3_dht20 import DHT20
from homebit3_lcd1602 import LCD1602 
from yolobit import *
import time
import sys      # THÊM: Thư viện hệ thống để đọc cổng USB
import uselect  # THÊM: Thư viện lắng nghe tín hiệu

dht20 = DHT20()

lcd = LCD1602()
lcd.clear()
lcd.move_to(0, 0)
lcd.putstr("YoloHome Active")

last_read_time = 0
cmd_buffer = "" 

# Thiết lập "đôi tai" để nghe ngóng cổng USB (Thay thế cho UART0)
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

while True:
    # --- KHỐI 1: LẮNG NGHE LỆNH TỪ USB CHUẨN MICROPYTHON ---
    # Kiểm tra xem máy tính có gửi chữ nào xuống không (timeout=0 để không bị đứng mạch)
    if spoll.poll(0):
        try:
            # Đọc 1 ký tự từ cáp USB
            char = sys.stdin.read(1)
            
            if char:
                # Ép hiển thị chữ 'cc' ra LCD như bạn muốn để test xem có lọt vào được đây không
                # lcd.putstr("cc") 
                
                cmd_buffer += char
                
                while "!" in cmd_buffer and "#" in cmd_buffer:
                    start = cmd_buffer.find("!")
                    end = cmd_buffer.find("#")
                    
                    if start < end:
                        msg = cmd_buffer[start:end] 
                        
                        if msg.startswith("!LCD:"):
                            lcd_text = msg[5:] 
                            lcd.clear()
                            lcd.move_to(0, 0)
                            lcd.putstr(lcd_text[:16])
                            
                            # Báo cáo ngược lên máy tính
                            print(f"!DEBUG:Da hien thi {lcd_text}#")
                            
                    cmd_buffer = cmd_buffer[end + 1:]
        except Exception as e:
            pass 
            
    # --- KHỐI 2: ĐỌC VÀ GỬI NHIỆT ĐỘ LÊN WEB ---
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_read_time) >= 3000:
        temp = dht20.dht20_temperature()
        payload = f"!SENSORS:TEMP:{temp}#"
        print(payload)
        last_read_time = current_time
        
    time.sleep_ms(50)