# Web Architecture Design - Dubbing Extractor v3

## Tổng quan

Migrate từ Tkinter desktop app sang web architecture để giải quyết vấn đề UI blocking.

## Kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Source  │  Adjust  │   Dub    │   Log    │  Status  │  │
│  │   Tab    │   Tab    │   Tab    │   Tab    │   Bar    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                          │                                   │
│                    WebSocket Client                          │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              REST API Endpoints                       │  │
│  │  POST /api/process    - Start processing             │  │
│  │  POST /api/step/{n}   - Run step n                   │  │
│  │  GET  /api/status     - Get current status           │  │
│  │  GET  /api/preview    - Get video preview info       │  │
│  │  POST /api/tts/test   - Test TTS voice               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            WebSocket Server (/ws)                     │  │
│  │  - Real-time progress updates                        │  │
│  │  - Log streaming                                     │  │
│  │  - Status notifications                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Background Task Queue (Celery)                │  │
│  │  - Video download                                    │  │
│  │  - Whisper transcription                             │  │
│  │  - Translation                                       │  │
│  │  - FFmpeg encoding                                   │  │
│  │  - TTS dubbing                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Existing Python Modules                    │
│  - workflow.py (step1-7 functions)                          │
│  - downloader/ (yt-dlp wrapper)                             │
│  - transcription/ (Whisper, translator)                     │
│  - video_processing/ (FFmpeg, subtitle detector)            │
│  - tts/ (VieNeu-TTS)                                        │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool (fast HMR)
- **TailwindCSS** - Styling (giống theme hiện tại)
- **Zustand** - State management (lightweight)
- **React Query** - API data fetching
- **Socket.IO Client** - WebSocket connection

### Backend
- **FastAPI** - Web framework
- **Celery** - Background task queue
- **Redis** - Message broker cho Celery + cache
- **Socket.IO** - WebSocket server
- **Pydantic** - Data validation

### Deployment
- **Docker Compose** - Orchestration
- **Nginx** - Reverse proxy (serve React build + proxy API)

## API Design

### REST Endpoints

```python
# Video Processing
POST /api/process
{
  "source": "https://youtube.com/watch?v=...",
  "mode": "monolithic",  # or "step-by-step"
  "options": {
    "whisper_model": "medium",
    "cover_mode": "blur",
    "burn_subtitle": true,
    "enable_dubbing": true,
    "tts_voice": "female_north"
  }
}
Response: {"task_id": "abc123", "status": "queued"}

# Step-by-step mode
POST /api/step/1
{"task_id": "abc123", "source": "..."}
Response: {"status": "running", "step": 1}

# Get status
GET /api/status/{task_id}
Response: {
  "task_id": "abc123",
  "status": "running",  # queued, running, completed, failed
  "current_step": 2,
  "progress": 45,
  "message": "Transcribing audio...",
  "outputs": {...}
}

# Preview info
POST /api/preview
{"source": "https://..."}
Response: {
  "title": "Video Title",
  "duration": 120.5,
  "thumbnail": "https://...",
  "platform": "youtube"
}

# TTS test
POST /api/tts/test
{"text": "Xin chào", "voice": "female_north"}
Response: {"audio_url": "/api/audio/temp123.wav"}
```

### WebSocket Events

```javascript
// Client → Server
socket.emit('subscribe', {task_id: 'abc123'})

// Server → Client
socket.on('progress', {
  task_id: 'abc123',
  step: 2,
  progress: 45,
  message: 'Transcribing audio...'
})

socket.on('log', {
  task_id: 'abc123',
  level: 'info',
  message: 'Downloaded video: 1920x1080'
})

socket.on('completed', {
  task_id: 'abc123',
  outputs: {
    video_clean: '/output/abc123/clean.mp4',
    video_dubbed: '/output/abc123/dubbed.mp4',
    srt_original: '/output/abc123/original.srt',
    srt_translated: '/output/abc123/translated.srt'
  }
})

socket.on('error', {
  task_id: 'abc123',
  error: 'FFmpeg encoding failed'
})
```

## Component Mapping

### Tkinter → React

| Tkinter Component | React Component |
|-------------------|-----------------|
| `SourceView` | `<SourceTab />` |
| `AdjustView` | `<AdjustTab />` |
| `DubView` | `<DubTab />` |
| `LogView` | `<LogTab />` |
| `EnhancedProgressBar` | `<ProgressBar />` |
| `LoadingOverlay` | `<LoadingSpinner />` |
| `StatusNotifier` | `<Toast />` (react-hot-toast) |

### State Management

```javascript
// Zustand store
const useAppStore = create((set) => ({
  // Current task
  taskId: null,
  status: 'idle',
  currentStep: 0,
  progress: 0,
  message: '',
  
  // Outputs
  outputs: {},
  
  // Logs
  logs: [],
  
  // Actions
  startProcessing: async (options) => {...},
  runStep: async (step) => {...},
  updateProgress: (data) => {...},
  addLog: (log) => {...}
}))
```

## Background Tasks

### Celery Task Structure

```python
# tasks.py
from celery import Celery, Task
from celery.signals import task_prerun, task_postrun

app = Celery('dubbing', broker='redis://localhost:6379/0')

class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        # Emit WebSocket event
        socketio.emit('completed', {'task_id': task_id, 'outputs': retval})
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        socketio.emit('error', {'task_id': task_id, 'error': str(exc)})

@app.task(base=CallbackTask, bind=True)
def process_video_task(self, source, options):
    """Run full pipeline in background."""
    def progress_callback(step, progress, message):
        # Emit WebSocket event
        socketio.emit('progress', {
            'task_id': self.request.id,
            'step': step,
            'progress': progress,
            'message': message
        })
    
    # Reuse existing workflow.py
    result = process_video(
        source=source,
        output_dir=f"output/{self.request.id}",
        log_cb=lambda msg: socketio.emit('log', {
            'task_id': self.request.id,
            'message': msg
        }),
        progress_cb=progress_callback,
        **options
    )
    return result

@app.task(base=CallbackTask, bind=True)
def run_step_task(self, step_num, task_id, **kwargs):
    """Run single step in background."""
    step_functions = {
        1: step1_prepare,
        2: step2_transcribe,
        3: step3_translate,
        4: step4_cover,
        5: step5_export,
        6: step6_burn,
        7: step7_dub
    }
    
    func = step_functions[step_num]
    result = func(
        log_cb=lambda msg: socketio.emit('log', {'task_id': task_id, 'message': msg}),
        **kwargs
    )
    return result
```

## Migration Strategy

### Phase 1: Backend API (Week 1)
1. ✅ Setup FastAPI project structure
2. ✅ Implement REST endpoints
3. ✅ Setup Celery + Redis
4. ✅ Integrate existing workflow.py
5. ✅ Add WebSocket support
6. ✅ Test API với Postman/curl

### Phase 2: Frontend (Week 2)
1. ✅ Setup React + Vite project
2. ✅ Create component library (matching current UI)
3. ✅ Implement tabs (Source, Adjust, Dub, Log)
4. ✅ Add WebSocket client
5. ✅ Connect to backend API
6. ✅ Test UI flow

### Phase 3: Integration (Week 3)
1. ✅ Docker Compose setup
2. ✅ Nginx reverse proxy
3. ✅ File upload/download handling
4. ✅ Error handling & retry logic
5. ✅ Production build & optimization

### Phase 4: Polish (Week 4)
1. ✅ UI/UX improvements
2. ✅ Performance optimization
3. ✅ Testing (unit + integration)
4. ✅ Documentation
5. ✅ Deployment guide

## File Structure

```
dubbing-extractor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── tasks.py             # Celery tasks
│   │   ├── websocket.py         # Socket.IO handlers
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── process.py       # Processing endpoints
│   │   │   ├── preview.py       # Preview endpoints
│   │   │   └── tts.py           # TTS endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic models
│   │   └── core/
│   │       ├── __init__.py
│   │       └── config.py        # Settings
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SourceTab.jsx
│   │   │   ├── AdjustTab.jsx
│   │   │   ├── DubTab.jsx
│   │   │   ├── LogTab.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Toast.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useProcessing.js
│   │   ├── store/
│   │   │   └── appStore.js      # Zustand store
│   │   ├── api/
│   │   │   └── client.js        # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── src/                          # Existing Python modules (reused)
│   ├── modules/
│   │   ├── workflow.py
│   │   ├── downloader/
│   │   ├── transcription/
│   │   ├── video_processing/
│   │   └── tts/
│   └── utils/
│
├── docker-compose.yml
├── nginx.conf
└── README_WEB.md
```

## Advantages

### ✅ Giải quyết UI blocking
- Background tasks chạy trong Celery workers
- UI luôn responsive
- Real-time progress updates qua WebSocket

### ✅ Scalability
- Có thể chạy nhiều workers song song
- Redis cache giảm load
- Horizontal scaling dễ dàng

### ✅ Better UX
- Modern web UI
- Responsive design (mobile-friendly)
- Smooth animations
- Better error handling

### ✅ Reuse existing code
- Tất cả logic trong `src/modules/` giữ nguyên
- Chỉ thêm API layer
- Không cần rewrite core functionality

## Next Steps

1. **Immediate**: Setup FastAPI backend với basic endpoints
2. **Then**: Add Celery + Redis cho background tasks
3. **Then**: Create React frontend với basic UI
4. **Finally**: Connect frontend ↔ backend qua WebSocket

Bạn muốn bắt đầu từ đâu?
- [ ] Setup FastAPI backend
- [ ] Setup React frontend
- [ ] Setup Docker Compose
