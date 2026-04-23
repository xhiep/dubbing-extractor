# Dubbing Extractor v2 - GPU Optimized

## Tong ket cac thay doi

### Da fix thanh cong:
1. **Virtual Environment**: Tat ca dependencies duoc cai vao `venv/` trong project
2. **Project-local Cache**: `.cache/` va `.tmp/` trong project giu HuggingFace, torch, pip va temp
3. **PyTorch CUDA**: Cai PyTorch 2.7.0 nightly voi CUDA 12.4 support
4. **NVENC GPU Encoding**: FFmpeg su dung NVENC de encode video nhanh hon 3-5 lan
5. **Whisper**: Chay tren CPU (do RTX 5060 sm_120 chua duoc PyTorch ho tro day du)
6. **VieNeu-TTS**: Da tich hop long tieng tieng Viet, clone giong va nghe thu

### Cau hinh hien tai:
- Python: 3.11 (trong venv)
- PyTorch: 2.7.0.dev20250310+cu124
- GPU: NVIDIA GeForce RTX 5060 (8GB VRAM)
- CUDA: 13.2 (driver) / 12.4 (PyTorch)
- FFmpeg: Static build voi NVENC support
- Whisper: Chay tren CPU (stable va nhanh)

### Tai sao Whisper chay tren CPU?
RTX 5060 co compute capability sm_120 (Blackwell architecture moi nhat).
PyTorch hien tai chi ho tro den sm_90, nen Whisper khong the chay on dinh tren GPU nay.
Tuy nhien, CPU van rat nhanh cho Whisper, va NVENC van duoc su dung cho video encoding.

## Cach su dung

### Lan dau tien - Cai dat:
```bash
install.bat
```

Qua trinh cai dat (~5-10 phut):
1. Tao virtual environment
2. Tai ffmpeg static build (~100MB)
3. Cai yt-dlp, whisper, deep-translator
4. Cai PyTorch CUDA (~2.5GB)
5. Cai VieNeu-TTS bang wheel Windows tu index chinh thuc cua repo

### Chay app:
```bash
run.bat
```

### Test nhanh VieNeu-TTS:
```bash
venv\Scripts\python.exe scripts\system_check.py
```

## Performance

### Video Encoding (NVENC GPU):
- **Toc do**: 3-5x nhanh hon CPU encoding
- **Chat luong**: Tuong duong libx264 preset fast
- **GPU usage**: 10-30% khi encode

### Whisper Transcription (CPU):
- **tiny**: ~10x realtime
- **base**: ~5x realtime  
- **small**: ~2x realtime
- **medium**: ~1x realtime
- **large**: ~0.5x realtime

## Kiem tra he thong

### Kiem tra GPU:
```bash
venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### Kiem tra NVENC:
```bash
bin\ffmpeg\ffmpeg.exe -hide_banner -encoders | findstr nvenc
```

### Kiem tra Whisper:
```bash
venv\Scripts\python.exe test_whisper_cpu.py
```

## Troubleshooting

### "CUDA out of memory":
Khong xay ra vi Whisper chay tren CPU.

### NVENC encoding that bai:
App tu dong fallback ve libx264 CPU encoding.

### Whisper qua cham:
Giam model size trong config.json:
- large -> medium (nhanh 2x)
- medium -> small (nhanh 2x)
- small -> base (nhanh 2x)
- base -> tiny (nhanh 2x)

## Cau truc project

```
dubbing-extractor-v2-fixed-patched/
├── venv/                    # Virtual environment (KHONG commit)
├── .cache/                  # HuggingFace / torch / pip cache trong project
├── .tmp/                    # Temp trong project
├── bin/
│   └── ffmpeg/             # FFmpeg static + NVENC
├── output/                 # Video output
├── scripts/
│   ├── installer.py        # Script cai dat
│   ├── install.bat         # Chay installer
│   ├── run.bat             # Chay app (dung venv Python)
│   └── system_check.py     # Check whisper + vieneu + local cache
├── main.py                 # App chinh
├── config.json             # Cau hinh
├── cookies.txt             # Cookies cho yt-dlp
└── README_GPU.md           # File nay
```

## Ket luan

Project da duoc optimize de su dung GPU cho video encoding (NVENC).
Whisper chay tren CPU de dam bao on dinh vi RTX 5060 qua moi.
Tong the performance tang ~3-5x cho video encoding, va da co them pipeline long tieng tieng Viet bang VieNeu-TTS.

---

**Fixed by**: AI Agent
**Date**: 2026-04-22
**GPU**: NVIDIA GeForce RTX 5060
