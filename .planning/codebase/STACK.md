---
type: codebase-map
focus: tech
created: 2026-04-23
---

# Technology Stack

## Runtime Environment

**Python 3.11.9**
- Primary language for entire application
- Windows 10 Pro target platform
- Virtual environment managed via `venv/`

**Shell**: Bash (Git Bash on Windows)
- Scripts use Unix-style paths and commands
- PowerShell used for specific ffmpeg invocations

## Core Dependencies

### AI/ML Stack

**Whisper (openai-whisper==20250625)**
- Speech-to-text transcription engine
- Runs on CPU (RTX 5060 sm_120 not yet supported by PyTorch stable)
- Models: tiny, base, small, medium, large
- Located: `src/modules/transcription/whisper_engine.py`

**VieNeu-TTS (vieneu==2.4.3)**
- Vietnamese text-to-speech engine
- Two backends: turbo_gpu (llama.cpp GGUF) and standard (transformers)
- Models cached in `.cache/huggingface/hub/`
- Voice cloning support via reference audio
- Located: `src/modules/tts/vieneu_engine.py`

**PyTorch**
- Installed via nightly/cu128 index for CUDA support
- CPU-only for Whisper (GPU not yet compatible with sm_120)
- NVENC hardware encoding works for video

**Transformers Ecosystem**
- transformers==5.5.4
- accelerate==1.13.0
- peft==0.14.0
- huggingface_hub==1.11.0
- safetensors==0.7.0
- tokenizers==0.22.2

### Video/Audio Processing

**ffmpeg**
- Bundled binary at `bin/ffmpeg/ffmpeg.exe`
- NOT in system PATH
- Invoked via PowerShell wrapper: `powershell.exe -Command "& 'C:\Users\xhiep\Downloads\dubbing-extractor\bin\ffmpeg\ffmpeg.exe' ..."`
- Used for: audio extraction, video encoding, subtitle burning, NVENC hardware acceleration
- Wrapper: `src/modules/video_processing/ffmpeg_wrapper.py`

**yt-dlp (yt-dlp==2026.3.17)**
- Video download from YouTube, Bilibili, etc.
- Cookie support via `cookies.txt`
- Platform detection: `src/modules/downloader/platform_detector.py`
- Wrapper: `src/modules/downloader/ytdlp_wrapper.py`

**Audio Libraries**
- librosa==0.11.0 (audio analysis)
- soundfile==0.13.1 (I/O)
- pydub==0.25.1 (manipulation)
- audioread==3.1.0 (decoding)
- soxr==1.0.0 (resampling)

**Video/Image Libraries**
- opencv-python-headless==4.13.0.92 (video processing, subtitle detection)
- pillow==12.2.0 (image manipulation)

### Translation

**deep-translator==1.11.4**
- Google Translate backend
- English → Vietnamese translation
- Located: `src/modules/transcription/translator.py`

### TTS Engine Dependencies

**llama.cpp Integration**
- llama_cpp_python==0.3.16 (GGUF model inference)
- lmdeploy==0.12.3 (deployment)

**Audio Codecs**
- neucodec==0.0.5 (neural audio codec)
- fla-core==0.5.0 (flash linear attention)
- flash-linear-attention==0.5.0
- local-attention==1.11.2
- vector-quantize-pytorch==1.17.8

**Text Processing**
- sea-g2p==0.7.5 (grapheme-to-phoneme for Vietnamese)
- sentencepiece==0.2.1 (tokenization)
- tiktoken==0.12.0 (tokenization)

**Tensor Operations**
- einops==0.8.2
- einx==0.4.3
- torch-einops-utils==0.0.30
- hyper-connections==0.4.10

### ONNX Runtime

- onnxruntime==1.24.4 (CPU)
- onnxruntime-gpu==1.25.0 (GPU)

### Web/API (Optional)

**FastAPI Stack**
- fastapi==0.136.0
- uvicorn==0.45.0
- starlette==1.0.0

**Gradio**
- gradio==6.13.0
- gradio_client==2.5.0

**OpenAI Client**
- openai==2.32.0 (for remote TTS API mode)

### HTTP/Network

- requests==2.33.1
- httpx==0.28.1
- aiohttp==3.13.5
- urllib3==2.6.3
- certifi==2026.2.25

### Data/Serialization

- numpy==2.4.4
- pandas==3.0.2
- pyarrow==24.0.0
- omegaconf==2.3.0
- PyYAML==6.0.3
- orjson==3.11.8

### Utilities

- tqdm==4.67.3 (progress bars)
- regex==2026.4.4
- packaging==26.1
- filelock==3.29.0
- fsspec==2026.2.0
- psutil==7.2.2 (memory monitoring)
- rich==15.0.0 (terminal formatting)
- colorama==0.4.6 (Windows color support)
- click==8.3.2 (CLI)
- pydantic==2.13.3 (validation)

### Scientific Computing

- scipy==1.17.1
- scikit-learn==1.8.0
- networkx==3.6.1
- sympy==1.14.0
- numba==0.65.0
- llvmlite==0.47.0

### Distributed Computing

- ray==2.55.0
- diskcache==5.6.3

## GUI Framework

**Tkinter (stdlib)**
- Native Python GUI toolkit
- Custom component library in `src/components/`
- Theme system: `src/components/theme.py`
- State management: `src/components/hooks/state.py`

## Configuration

**config.json**
- Runtime settings (source URL, models, subtitle params, TTS settings)
- Loaded/saved via `src/config.py`

**cookies.txt**
- yt-dlp authentication cookies
- Netscape cookie format

**.env**
- Environment variables (not in version control)
- Example: `.env.example`

## Installation

**Automated Installer**
- `scripts/installer.py` - creates venv, downloads ffmpeg, installs PyTorch CUDA nightly
- `scripts/install.bat` - Windows batch wrapper
- `scripts/run.bat` - launch script

**System Check**
- `scripts/system_check.py` - validates environment

## Hardware Acceleration

**NVIDIA RTX 5060 (Blackwell sm_120)**
- NVENC video encoding: ✅ works
- CUDA for Whisper: ❌ not yet supported (uses CPU)
- CUDA for TTS: ✅ works (turbo_gpu mode)

## Package Management

- `requirements.txt` - all dependencies
- PyTorch installed separately via nightly index
- Hugging Face models auto-downloaded to `.cache/`
