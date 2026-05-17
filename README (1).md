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





## 4. Trình tự chạy project

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



---

## 5. Seed user test

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

