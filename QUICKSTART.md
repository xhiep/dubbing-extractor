# Dubbing Extractor v3 - Quick Start Guide

## 🚀 Chạy Web App (Recommended)

### Cách 1: Docker Compose (Easiest)

```bash
# Clone repo
git clone <your-repo-url>
cd dubbing-extractor

# Start all services
docker-compose up

# Truy cập:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Cách 2: Manual (Development)

**Yêu cầu:**
- Python 3.11+
- Node.js 20+
- Redis

**Bước 1: Cài Redis**
```bash
# Windows: Download từ https://github.com/microsoftarchive/redis/releases
# hoặc dùng Docker:
docker run -d -p 6379:6379 redis:alpine
```

**Bước 2: Backend**
```bash
cd backend
pip install -r requirements.txt
start_server.bat  # Windows
# hoặc
./start_server.sh  # Linux/Mac
```

**Bước 3: Celery Worker** (Terminal mới)
```bash
cd backend
start_worker.bat  # Windows
# hoặc
./start_worker.sh  # Linux/Mac
```

**Bước 4: Frontend** (Terminal mới)
```bash
cd frontend
npm install
npm run dev
```

**Truy cập:** http://localhost:5173

---

## 🖥️ Chạy Desktop App (Tkinter - Old)

```bash
# Activate venv
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# Run
python main.py
```

---

## 📊 So sánh Web vs Desktop

| Feature | Desktop (Tkinter) | Web (React + FastAPI) |
|---------|-------------------|------------------------|
| UI Blocking | ❌ Đơ khi xử lý | ✅ Luôn responsive |
| Real-time Updates | ❌ Polling | ✅ WebSocket |
| Multi-tasking | ❌ Single task | ✅ Multiple workers |
| Mobile Support | ❌ No | ✅ Yes |
| Deployment | ❌ Desktop only | ✅ Docker + Cloud |

---

## 🎯 Tính năng chính

### Pipeline xử lý video (7 bước)

1. **Chuẩn bị**: Download video (yt-dlp) hoặc dùng file local
2. **Transcribe**: Whisper (CPU) → SRT gốc
3. **Dịch**: Google Translate → SRT tiếng Việt
4. **Che phụ đề**: Blur/blackbar phụ đề gốc
5. **Xuất file**: SRT, script, song ngữ
6. **Burn subtitle**: Đốt phụ đề vào video
7. **Lồng tiếng**: VieNeu-TTS (optional)

### Hai chế độ xử lý

- **Monolithic**: Chạy toàn bộ pipeline tự động
- **Step-by-step**: Chạy từng bước, có thể edit SRT giữa chừng

---

## 📁 Cấu trúc Project

```
dubbing-extractor/
├── main.py                 # Desktop app (Tkinter)
├── backend/                # Web backend (FastAPI)
├── frontend/               # Web frontend (React)
├── src/                    # Core modules (shared)
│   ├── modules/
│   │   ├── workflow.py     # Pipeline logic
│   │   ├── downloader/     # yt-dlp wrapper
│   │   ├── transcription/  # Whisper + translator
│   │   ├── video_processing/  # FFmpeg
│   │   └── tts/            # VieNeu-TTS
│   └── utils/
├── docker-compose.yml      # Docker orchestration
└── output/                 # Output files
```

---

## 🔧 Troubleshooting

### Redis connection error
```bash
redis-cli ping  # Should return: PONG
```

### Celery worker not starting
```bash
# Check Redis connection
celery -A app.tasks:celery_app inspect ping
```

### Frontend not connecting to backend
- Check `vite.config.js` proxy settings
- Ensure backend is running on port 8000

### FFmpeg not found
- Desktop app: `bin\ffmpeg\ffmpeg.exe`
- Docker: FFmpeg included in backend image

---

## 📚 Documentation

- [Web Architecture](docs/WEB_ARCHITECTURE.md)
- [Backend API](backend/README.md)
- [Original Tkinter App](CLAUDE.md)

---

## 🎓 Next Steps

1. ✅ Web architecture complete
2. ⏳ Test full pipeline with real video
3. ⏳ Production optimization
4. ⏳ Deploy to cloud (AWS/GCP/Azure)

---

## 📝 Notes

- **GPU**: RTX 5060 (sm_120) - Whisper dùng CPU, NVENC encoding OK
- **TTS**: VieNeu-TTS chỉ hỗ trợ tiếng Việt
- **Output**: `output/` directory cho cả desktop và web app
