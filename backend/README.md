# FastAPI Backend

Backend API cho Dubbing Extractor v3 với FastAPI + Celery + WebSocket.

## Cài đặt

### 1. Cài dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Cài Redis (Windows)

Download Redis for Windows:
- https://github.com/microsoftarchive/redis/releases
- Hoặc dùng Docker: `docker run -d -p 6379:6379 redis:alpine`

### 3. Cấu hình

Copy `.env.example` thành `.env`:

```bash
cp .env.example .env
```

## Chạy Backend

### Cách 1: Manual (3 terminals)

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - FastAPI:**
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

### Cách 2: Docker Compose (recommended)

```bash
docker-compose up
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
GET /health
```

### Video Processing

**Start Processing (Monolithic):**
```bash
POST /api/process
Content-Type: application/json

{
  "source": "https://youtube.com/watch?v=...",
  "mode": "monolithic",
  "whisper_model": "medium",
  "cover_mode": "blur",
  "burn_subtitle": true,
  "enable_dubbing": true,
  "tts_voice": "female_north"
}

Response:
{
  "task_id": "abc123",
  "status": "queued",
  "message": "Processing started"
}
```

**Run Single Step:**
```bash
POST /api/process/step/1
Content-Type: application/json

{
  "task_id": "abc123",
  "step_data": {
    "source": "https://..."
  }
}
```

**Get Status:**
```bash
GET /api/process/status/{task_id}

Response:
{
  "task_id": "abc123",
  "status": "running",
  "current_step": 2,
  "progress": 45.0,
  "message": "Transcribing audio...",
  "outputs": {},
  "error": null
}
```

**Cancel Task:**
```bash
POST /api/process/cancel/{task_id}
```

### Preview

**Get Video Info:**
```bash
POST /api/preview
Content-Type: application/json

{
  "source": "https://youtube.com/watch?v=..."
}

Response:
{
  "title": "Video Title",
  "duration": 120.5,
  "thumbnail": "https://...",
  "platform": "youtube",
  "width": 1920,
  "height": 1080
}
```

### TTS

**List Voices:**
```bash
GET /api/tts/voices

Response:
{
  "voices": ["female_north", "female_south", "male_north", "male_south"]
}
```

**Test Voice:**
```bash
POST /api/tts/test
Content-Type: application/json

{
  "text": "Xin chào",
  "voice": "female_north"
}

Response:
{
  "audio_url": "/api/tts/audio/abc123",
  "duration": 1.5
}
```

## WebSocket

### Connect

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  path: '/ws/socket.io',
});

socket.on('connect', () => {
  console.log('Connected to server');
});
```

### Subscribe to Task

```javascript
socket.emit('subscribe', { task_id: 'abc123' });

socket.on('subscribed', (data) => {
  console.log('Subscribed to task:', data.task_id);
});
```

### Events

**Progress Update:**
```javascript
socket.on('progress', (data) => {
  console.log(`Step ${data.step}: ${data.progress}% - ${data.message}`);
});
```

**Log Message:**
```javascript
socket.on('log', (data) => {
  console.log(`[${data.level}] ${data.message}`);
});
```

**Task Completed:**
```javascript
socket.on('completed', (data) => {
  console.log('Task completed:', data.outputs);
});
```

**Error:**
```javascript
socket.on('error', (data) => {
  console.error(`Error in step ${data.step}: ${data.error}`);
});
```

## Architecture

```
FastAPI (port 8000)
  ├── REST API endpoints
  ├── WebSocket server (Socket.IO)
  └── Static file serving (/output)

Celery Workers
  ├── process_video_task (monolithic)
  └── run_step_task (step-by-step)

Redis (port 6379)
  ├── Message broker (Celery)
  └── Result backend (Celery)
```

## Development

### Run with auto-reload

```bash
uvicorn app.main:asgi_app --reload --host 0.0.0.0 --port 8000
```

### Test API

```bash
# Install httpie
pip install httpie

# Test health
http GET http://localhost:8000/health

# Test preview
http POST http://localhost:8000/api/preview source="https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### View Celery tasks

```bash
celery -A app.tasks:celery_app inspect active
celery -A app.tasks:celery_app inspect stats
```

## Troubleshooting

### Redis connection error

Đảm bảo Redis đang chạy:
```bash
redis-cli ping
# Should return: PONG
```

### Celery worker not starting

Check Redis connection trong `.env`:
```
CELERY_BROKER_URL=redis://localhost:6379/0
```

### WebSocket not connecting

Check CORS settings trong `app/core/config.py`:
```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
]
```

## Next Steps

1. ✅ Backend API hoàn thành
2. ⏳ Tạo React frontend
3. ⏳ Docker Compose setup
4. ⏳ Integration testing
