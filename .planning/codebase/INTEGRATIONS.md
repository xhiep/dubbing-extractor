---
type: codebase-map
focus: integrations
created: 2026-04-23
---

# External Integrations

## Video Platforms

**YouTube**
- Download via yt-dlp
- Cookie authentication support (`cookies.txt`)
- Platform detection: `src/modules/downloader/platform_detector.py`

**Bilibili**
- Download via yt-dlp
- Cookie authentication required for some content
- Example URL in config: `https://www.bilibili.com/video/BV11sBvBqE8H`

**Generic Video Platforms**
- Any platform supported by yt-dlp
- Local file support (MP4, MKV, etc.)
- Detection: `src/utils/file_utils.is_local_file()`

## AI/ML Services

**Hugging Face Hub**
- Model downloads via `huggingface_hub==1.11.0`
- Cached in `.cache/huggingface/hub/`
- Models used:
  - `pnnbao-ump/VieNeu-TTS` (Vietnamese TTS)
  - `pnnbao-ump/VieNeu-TTS-v2-Turbo` (faster variant)
  - `pnnbao-ump/VieNeu-TTS-0.3B-q4-gguf` (quantized)
  - `pnnbao-ump/VieNeu-TTS-v2-Turbo-GGUF` (quantized turbo)
  - `neuphonic/distill-neucodec` (audio codec)
  - `ntu-spml/distilhubert` (audio features)

**OpenAI Whisper**
- Local inference (no API calls)
- Models downloaded automatically on first use
- CPU-only execution

**Google Translate**
- Via `deep-translator` library
- No API key required (uses public endpoint)
- English → Vietnamese translation
- Located: `src/modules/transcription/translator.py`

## Remote TTS API (Optional)

**OpenAI-Compatible API**
- Configurable endpoint: `dub_remote_api_base` in `config.json`
- Default: `http://localhost:23333/v1`
- Used when `dub_mode` is set to remote API mode
- Client: `openai==2.32.0`

## File System

**Output Directory**
- `output/` - all generated files
- Structure: `output/{video_title}_{timestamp}/`
- Contains: video, audio, SRT, scripts, logs

**Cache Directory**
- `.cache/` - Hugging Face models, pip cache
- `.tmp/` - temporary processing files

**Binary Directory**
- `bin/ffmpeg/` - bundled ffmpeg executable
- Not in system PATH

## Configuration Files

**config.json**
- Runtime settings persistence
- JSON format
- Auto-saved on UI changes

**cookies.txt**
- Netscape cookie format
- Used by yt-dlp for authenticated downloads
- Platform-specific cookies (YouTube, Bilibili, etc.)

**.env**
- Environment variables
- Not tracked in git
- Template: `.env.example`

## No External Databases

- All state stored in JSON files
- No SQL/NoSQL databases
- No external caching services (Redis, Memcached)

## No Cloud Services

- All processing runs locally
- No AWS/GCP/Azure integrations
- No cloud storage (S3, GCS, etc.)
- No cloud AI APIs (except optional remote TTS)

## Network Requirements

**Required**:
- Internet for video downloads (yt-dlp)
- Internet for model downloads (Hugging Face)
- Internet for translation (Google Translate)

**Optional**:
- Remote TTS API endpoint (if configured)

**Not Required**:
- No telemetry/analytics
- No license validation
- No update checks
