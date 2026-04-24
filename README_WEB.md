# Dubbing Extractor v3 - Web Architecture

## 🎯 Tổng quan

Migrate từ Tkinter desktop app sang web architecture với:
- **Frontend**: React + Vite + TailwindCSS
- **Backend**: FastAPI + Celery + Redis
- **Real-time**: WebSocket (Socket.IO)
- **Deployment**: Docker Compose

## 🚀 Quick Start

### 1. Cài đặt Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Chạy với Docker Compose (Recommended)

```bash
docker-compose up
```

Truy cập:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Chạy Manual (Development)

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Backend:**
```bash
cd backend
start_server.bat  # Windows
# hoặc
./start_server.sh  # Linux/Mac
```

**Terminal 3 - Celery Worker:**
```bash
cd backend
start_worker.bat  # Windows
# hoặc
./start_worker.sh  # Linux/Mac
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

## 📁 Cấu trúc Project

```
dubbing-extractor/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST endpoints
│   │   │   ├── process.py     # Video processing
│   │   │   ├── preview.py     # Preview info
│   │   │   └── tts.py         # TTS testing
│   │   ├── core/
│   │   │   └── config.py      # Settings
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic models
│   │   ├── main.py            # FastAPI app
│   │   ├── tasks.py           # Celery tasks
│   │   └── websocket.py       # Socket.IO handlers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── SourceTab.jsx
│   │   │   ├── AdjustTab.jsx
│   │   │   ├── DubTab.jsx
│   │   │   ├── LogTab.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── StatusBar.jsx
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── useWebSocket.js
│   │   │   └── useProcessing.js
│   │   ├── store/             # Zustand store
│   │   │   └── appStore.js
│   │   ├── api/               # API client
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── src/                        # Existing Python modules (reused)
│   ├── modules/
│   │   ├── workflow.py        # Core pipeline
│   │   ├── downloader/
│   │   ├── transcription/
│   │   ├── video_processing/
│   │   └── tts/
│   └── utils/
│
├── docker-compose.yml          # Docker orchestration
├── nginx.conf                  # Reverse proxy config
└── docs/
    └── WEB_ARCHITECTURE.md     # Architecture design doc
```

## 🔧 Tính năng

### ✅ Đã hoàn thành

1. **Backend API**
   - REST endpoints cho video processing
   - WebSocket real-time updates
   - Celery background tasks
   - Preview video info
   - TTS voice testing

2. **Frontend UI**
   - 4 tabs: Source, Adjust, Dub, Log
   - Real-time progress bar
   - WebSocket connection
   - Toast notifications
   - Responsive design

3. **Infrastructure**
   - Docker Compose setup
   - Nginx reverse proxy
   - Redis message broker

### 🎯 Advantages vs Tkinter

| Feature | Tkinter (Old) | Web (New) |
|---------|---------------|-----------|
| UI Blocking | ❌ Đơ khi xử lý | ✅ Luôn responsive |
| Real-time Updates | ❌ Polling | ✅ WebSocket |
| Scalability | ❌ Single process | ✅ Multiple workers |
| Deployment | ❌ Desktop only | ✅ Web + Docker |
| Mobile Support | ❌ No | ✅ Yes (responsive) |
| Modern UI | ❌ Tkinter widgets | ✅ React + Tailwind |

## 📊 Architecture Flow

```
User Browser
    ↓
React Frontend (port 5173)
    ↓ HTTP/WebSocket
FastAPI Backend (port 8000)
    ↓ Task Queue
Celery Workers
    ↓ Execute
Python Modules (workflow.py, etc.)
    ↓ Results
WebSocket → Frontend
```

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Preview video
curl -X POST http://localhost:8000/api/preview \
  -H "Content-Type: application/json" \
  -d '{"source": "https://youtube.com/watch?v=dQw4w9WgXcQ"}'

# Start processing
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "source": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "mode": "monolithic",
    "whisper_model": "medium",
    "cover_mode": "blur"
  }'
```

### Test WebSocket

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  path: '/ws/socket.io',
});

socket.on('connect', () => console.log('Connected'));
socket.emit('subscribe', { task_id: 'abc123' });
socket.on('progress', (data) => console.log(data));
```

## 🐛 Troubleshooting

### Redis connection error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

### Celery worker not starting
```bash
# Check Redis connection
celery -A app.tasks:celery_app inspect ping
```

### WebSocket not connecting
- Check CORS settings in `backend/app/core/config.py`
- Ensure frontend proxy is configured in `vite.config.js`

### Docker build fails
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 📝 Next Steps

1. ✅ Backend API - DONE
2. ✅ Frontend UI - DONE
3. ✅ Docker Compose - DONE
4. ⏳ Integration testing
5. ⏳ Production optimization
6. ⏳ Deployment guide

## 🎓 Migration Guide

### Từ Tkinter sang Web

**Old (Tkinter):**
```python
# main.py - 2,043 lines
def on_start_button_click():
    # Blocks UI thread
    result = process_video(...)
    update_ui(result)
```

**New (Web):**
```python
# backend/app/tasks.py
@celery_app.task
def process_video_task(source, options):
    # Runs in background worker
    result = process_video(...)
    emit_completed(task_id, result)
```

```javascript
// frontend/src/hooks/useProcessing.js
const { start } = useProcessing()
start() // Non-blocking, returns immediately
```

## 📚 Documentation

- [Backend API](backend/README.md)
- [Architecture Design](docs/WEB_ARCHITECTURE.md)
- [Original Tkinter App](main.py)

## 🤝 Contributing

1. Backend changes: `backend/app/`
2. Frontend changes: `frontend/src/`
3. Core logic: `src/modules/` (shared with Tkinter app)

## 📄 License

Same as original Dubbing Extractor project.
