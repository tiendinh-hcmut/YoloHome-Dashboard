# YOLOHome Fullstack

Hệ thống fullstack cho:
- **Vision AI**: nhận diện cháy/khói từ ảnh, video, webcam
- **IoT Dashboard**: hiển thị sensor, điều khiển thiết bị
- **Adafruit IO + Gateway + YoloBit/ESP32**: đồng bộ dữ liệu và điều khiển pump

---

## 1. Kiến trúc tổng quát

### Vision
Webcam / Image / Video  
→ Frontend React  
→ Backend FastAPI  
→ YOLO detect fire/smoke  
→ Gửi trạng thái danger lên **Adafruit IO**  
→ Gateway đọc feed  
→ Gửi lệnh xuống **YoloBit / ESP32**  
→ Bật / tắt pump

### IoT
YoloBit / ESP32 đọc sensor  
→ gửi qua Serial cho Gateway  
→ publish lên Adafruit / hoặc backend đồng bộ vào MongoDB  
→ Frontend hiển thị trên dashboard

---

## 2. Tính năng chính

- Detect ảnh: `POST /api/detect-image`
- Detect video: `POST /api/detect-video`
- Detect frame webcam: `POST /api/detect-frame`
- Auto detect webcam liên tục
- Khi detect ra `fire / smoke / danger`:
  - publish `danger-detected = 1`
  - publish `pump-command = 1`
- Nếu không còn danger:
  - giữ pump ON thêm **10 giây**
  - sau đó mới publish `pump-command = 0`
- IoT dashboard đọc dữ liệu sensor từ MongoDB
- Gateway nhận lệnh từ Adafruit IO và gửi xuống YoloBit qua Serial

---

## 3. Yêu cầu cài đặt

- Python 3.11 hoặc 3.12
- Node.js 18+
- MongoDB chạy local
- `best.pt` đặt trong:

```txt
backend/model/best.pt
```

---

## 4. Cấu trúc thư mục chính

```txt
backend/
  app/
    api/
    core/
    services/
  model/
  outputs/

frontend/
  src/
    components/
    pages/
    services/

gateway.py
```

---

## 5. Biến môi trường backend

Tạo file:

```txt
backend/.env
```

Nội dung mẫu:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=yolohome

JWT_SECRET_KEY=change_this_to_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SENSOR_TTL_SECONDS=2592000

ADAFRUIT_IO_USERNAME=YOUR_ADAFRUIT_USERNAME
ADAFRUIT_IO_KEY=YOUR_REAL_AIO_KEY

ADAFRUIT_IO_TEMP_FEED_KEY=bbc-temp
ADAFRUIT_IO_HUMIDITY_FEED_KEY=bbc-humidity
ADAFRUIT_IO_BRIGHTNESS_FEED_KEY=bbc-brightness

ADAFRUIT_IO_DANGER_FEED_KEY=danger-detected
ADAFRUIT_IO_PUMP_COMMAND_FEED_KEY=pump-command
ADAFRUIT_IO_PUMP_STATUS_FEED_KEY=pump-status
```

> Không commit `.env` hoặc API key thật lên GitHub.

---

## 6. Feed cần có trên Adafruit IO

Tạo các feed sau:

```txt
bbc-temp
bbc-humidity
bbc-brightness
bbc-lcd
bbc-led
danger-detected
pump-command
pump-status
```

---

## 7. Trình tự chạy project

### Terminal 1 — MongoDB
```powershell
mongod --dbpath C:\data\db
```

Nếu chưa có thư mục:
```powershell
mkdir C:\data\db
```

### Terminal 2 — Backend
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend:
```txt
http://localhost:8000
```

Swagger Docs:
```txt
http://localhost:8000/docs
```

### Terminal 3 — Frontend
```powershell
cd frontend
npm install
npm run dev
```

Frontend:
```txt
http://localhost:5173
```

### Terminal 4 — Gateway
```powershell
python gateway.py
```

---

## 8. Seed user test

Nếu cần tạo tài khoản mẫu:

```powershell
cd backend
python -m app.seed_users
```

Tài khoản test:
- `admin01 / 12345678`
- `operator01 / 12345678`
- `viewer01 / 12345678`

---

## 9. Gateway

Gateway chạy trên máy tính để:
- đọc dữ liệu Serial từ YoloBit
- publish sensor lên Adafruit
- subscribe lệnh từ Adafruit
- gửi lại lệnh xuống YoloBit

Ví dụ chạy:

```powershell
python gateway.py
```

Nếu board đang ở `COM8`, file `gateway.py` phải dùng đúng cổng đó.

---

## 10. File nạp vào YoloBit

Luồng hiện tại khuyến nghị:
- DHT20 dùng `SCL=20`, `SDA=19`
- pump điều khiển qua **P13**
- tự tắt sau **10 giây** nếu không có lệnh mới

Logic YoloBit:
- nhận `!PUMP:1#` → bật pump
- nhận `!PUMP:0#` → tắt pump
- gửi lại:
  - `!STATUS:PUMP:1#`
  - `!STATUS:PUMP:0#`

---

## 11. Logic Auto Detect Webcam

Frontend:
- mở webcam
- cứ mỗi khoảng **1–2 giây** chụp 1 frame
- gọi `POST /api/detect-frame`

Backend:
- detect frame
- nếu ra `fire / smoke / danger`:
  - `danger-detected = 1`
  - `pump-command = 1`
- nếu không danger:
  - chưa tắt pump ngay
  - giữ ON thêm **10 giây**
  - sau 10 giây mới gửi `pump-command = 0`

---

## 12. API chính

### Health
```http
GET /api/health
```

### Detect ảnh
```http
POST /api/detect-image
```

### Detect frame webcam
```http
POST /api/detect-frame
```

### Detect video
```http
POST /api/detect-video
```

### Test logic pump
```http
POST /api/alerts/test-pump
```

Body ví dụ:
```json
{
  "danger": true
}
```

---

## 13. Kiểm tra nhanh hệ thống

### Backend health
Mở:
```txt
http://localhost:8000/api/health
```

### Test publish Adafruit bằng backend
Vào:
```txt
http://localhost:8000/docs
```

Gọi:
```json
POST /api/alerts/test-pump
{
  "danger": true
}
```

Kỳ vọng:
- `danger-detected = 1`
- `pump-command = 1`

---

## 14. Lỗi thường gặp và cách xử lý

### 14.1. Adafruit lỗi 429 Too Many Requests
Nguyên nhân:
- gửi feed quá dày khi webcam autodetect liên tục

Cách xử lý:
- tăng interval autodetect lên `2000 ms`
- throttle publish ở backend
- chỉ publish khi giá trị đổi hoặc sau một khoảng refresh an toàn

---

### 14.2. `pump_status = 1` nhưng pump không chạy
Điều đó chỉ có nghĩa là **code đã nhận lệnh bật**, không chắc là pump đã được cấp điện thật.

Cần kiểm tra:
- đúng chân điều khiển chưa
- module điều khiển USB/pump có cấp điện ra chưa
- pump có chạy khi cắm trực tiếp vào USB máy tính không
- nguồn cấp có đủ dòng không

---

### 14.3. COM bị out khi bật pump
Dấu hiệu:
- `COM8` biến mất
- gateway báo reconnect
- board reset

Nguyên nhân:
- sụt nguồn
- pump kéo dòng lớn
- module điều khiển gây reset board

Cách xử lý:
- giữ YoloBit nối máy tính chỉ để Serial
- cấp nguồn ngoài ổn định cho phần pump/module
- test bằng tải nhẹ trước
- ưu tiên cổng điều khiển ổn định hơn như `P13`

---

### 14.4. DHT20 không nhận
Nếu `i2c.scan()` ra `[]`:
- kiểm tra lại SDA/SCL
- hiện tại bus đã xác nhận chạy ở:
  - `SCL = 20`
  - `SDA = 19`

---

### 14.5. GitHub chặn push vì lộ secret
Nếu gặp `GH013`:
- xóa key thật khỏi `.env`
- thay bằng placeholder
- đổi API key mới trên Adafruit
- commit lại sạch secret rồi mới push

---

## 15. Gợi ý vận hành ổn định

- Frontend autodetect mỗi **2 giây**
- Backend throttle publish Adafruit
- Gateway chỉ mở khi không có app nào khác giữ COM
- Không mở cùng lúc:
  - Thonny
  - Arduino Serial Monitor
  - app.ohstem
  - `gateway.py`

---

## 16. Ghi chú bảo mật

- Không đẩy `.env` lên GitHub
- Không public `ADAFRUIT_IO_KEY`
- Nếu lỡ lộ key, hãy **rotate key ngay**

---

## 17. Ghi chú cuối

Luồng hiện tại đã được tối ưu để:
- detect liên tục từ webcam
- giữ pump chạy liên tục khi còn danger
- chỉ tắt sau khi an toàn liên tục quá 10 giây
- hạn chế spam feed lên Adafruit

Nếu cần mở rộng:
- lưu log event danger vào MongoDB
- hiện lịch sử bật/tắt pump ở dashboard
- thêm relay/đèn/còi báo động
