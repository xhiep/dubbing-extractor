# Step-by-Step Pipeline UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tách `process_video` thành 7 hàm step riêng, thêm UI chạy từng bước (Bước 1–5) trong tab Nguồn, ô edit SRT sau bước dịch, và dọn duplicate checkbox lồng tiếng.

**Architecture:** `workflow.py` được tách thành 7 hàm `step1_*` … `step7_*` độc lập; `process_video` vẫn giữ nguyên API bằng cách gọi 7 hàm đó theo thứ tự. `main.py` thêm `pipeline_state` dict, 5 nút Bước 1–5 trong tab Nguồn (bấm Bước N = chạy từ đầu đến bước N), ô TextArea edit SRT xuất hiện sau khi Bước 3 xong, và xóa `quick_dub_toggle` duplicate.

**Tech Stack:** Python 3.11, Tkinter, yt-dlp, Whisper, Google Translate, ffmpeg (local bin)

---

## File Map

| File | Thay đổi |
|------|----------|
| `src/modules/workflow.py` | Tách thành 7 hàm step + giữ `process_video` |
| `main.py` | Xóa quick_dub_toggle; thêm pipeline_state, step buttons, SRT editor |

---

### Task 1: Tách `workflow.py` — helper nội bộ + step 1 & 2

**Files:**
- Modify: `src/modules/workflow.py`

- [ ] **Step 1: Đọc file workflow.py hiện tại để nắm cấu trúc**

```bash
# Đọc toàn bộ file để nhớ imports, helper functions, và logic step 1-2
```

- [ ] **Step 2: Thêm 7 hàm step vào đầu phần body của workflow.py**

Sau dòng `from ..config import config` (dòng 22), thêm toàn bộ các hàm step. Thêm `step1_download` và `step2_transcribe`:

```python
# ── Internal helpers ──────────────────────────────────────────────────────────

def _log_safe(log_cb, msg):
    if log_cb:
        try:
            log_cb(msg)
        except UnicodeEncodeError:
            log_cb(str(msg).encode("ascii", "replace").decode("ascii"))


def _apply_subtitle_timing(segments: list, subtitle_offset_sec: float,
                           subtitle_timing_scale: float, video_speed: float) -> list:
    adjusted = []
    scale = subtitle_timing_scale if subtitle_timing_scale > 0 else 1.0
    speed = video_speed if video_speed > 0 else 1.0
    effective_scale = scale / speed
    for seg in segments:
        start = max(0.0, float(seg["start"]) * effective_scale + subtitle_offset_sec)
        end = max(start + 0.05, float(seg["end"]) * effective_scale + subtitle_offset_sec)
        new_seg = dict(seg)
        new_seg["start"] = start
        new_seg["end"] = end
        adjusted.append(new_seg)
    return adjusted


def _retime_cover_events(detected_events: list, segments: list) -> list:
    import statistics
    if not detected_events:
        return []
    if not segments:
        return detected_events
    top_y = int(statistics.median(int(e["top_y"]) for e in detected_events))
    bottom_y = int(statistics.median(int(e["bottom_y"]) for e in detected_events))
    if bottom_y <= top_y:
        top_y = min(int(e["top_y"]) for e in detected_events)
        bottom_y = max(int(e["bottom_y"]) for e in detected_events)
    height = max(18, bottom_y - top_y + 1)
    retimed = []
    for seg in segments:
        start = max(0.0, float(seg.get("start", 0.0) or 0.0) - 0.04)
        end = max(start + 0.08, float(seg.get("end", 0.0) or 0.0) + 0.04)
        retimed.append({"start": start, "end": end,
                        "top_y": top_y, "bottom_y": bottom_y, "height": height})
    return retimed


# ── Step functions ─────────────────────────────────────────────────────────────

def step1_download(
    source_input: str,
    temp_dir: Path,
    log_cb: Optional[Callable] = None,
) -> tuple[Path, Path, str, Path]:
    """Download or use local file. Returns (raw_video, raw_audio, title, out_dir)."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 1: TAI VIDEO / SU DUNG FILE LOCAL\n{'='*52}")
    if is_local_file(source_input):
        raw_video = Path(source_input)
        title = raw_video.stem
        _log_safe(log_cb, f"->  File: {raw_video.name}  ({raw_video.stat().st_size/1024/1024:.1f} MB)")
        raw_audio = extract_audio_local(raw_video, temp_dir / "audio_goc.mp3", log_cb)
    else:
        raw_video, raw_audio, title = download(source_input, temp_dir, log_cb)

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = sanitize_filename(title)
    out_dir = Path(config.get("output_base_dir", "output")) / f"{safe_title}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    _log_safe(log_cb, f"✓  Output: {out_dir}")
    shutil.copy2(raw_audio, out_dir / "audio_goc.mp3")
    return raw_video, raw_audio, title, out_dir


def step2_transcribe(
    out_dir: Path,
    log_cb: Optional[Callable] = None,
) -> list:
    """Transcribe audio in out_dir/audio_goc.mp3. Returns segments list."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 2: NHAN DANG GIONG NOI (WHISPER)\n{'='*52}")
    segs = transcribe(out_dir / "audio_goc.mp3", log_cb)
    return segs
```

- [ ] **Step 3: Thêm `step3_translate`, `step4_cover`, `step5_export` vào workflow.py**

Tiếp tục sau `step2_transcribe`:

```python
def step3_translate(
    segs: list,
    subtitle_offset_sec: float = 0.0,
    subtitle_timing_scale: float = 1.0,
    video_speed: float = 1.0,
    log_cb: Optional[Callable] = None,
) -> list:
    """Translate segments to Vietnamese and apply timing. Returns segs_vi."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 3: DICH SANG TIENG VIET\n{'='*52}")
    if not segs:
        _log_safe(log_cb, "⚠  Whisper khong nhan dang duoc. Bo qua dich.")
        return []
    segs_vi = translate(segs, log_cb)
    if segs_vi:
        segs_vi = _apply_subtitle_timing(segs_vi, subtitle_offset_sec,
                                         subtitle_timing_scale, video_speed)
    return segs_vi


def step4_cover(
    raw_video: Path,
    segs_vi: list,
    out_dir: Path,
    cover_mode: str = "blur",
    blur_padding_px: int = 12,
    cover_offset_px: int = 0,
    blur_power: int = 4,
    video_speed: float = 1.0,
    log_cb: Optional[Callable] = None,
) -> tuple[Path, dict, int, int]:
    """Cover original subtitles. Returns (final_video, cover_meta, width, height)."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 4: CHE PHU DE GOC\n{'='*52}")
    valid_modes = ["none", "blur", "blackbar"]
    if cover_mode not in valid_modes:
        cover_mode = "blur"
    final_video = out_dir / "video_ready.mp4"
    w, h = get_dims(raw_video)
    detected_events = detect_sub_events(raw_video, w, h, log_cb)
    timed_cover_events = _retime_cover_events(detected_events, segs_vi)
    if timed_cover_events and detected_events:
        _log_safe(log_cb, f"->  Dung vi tri sub cu da detect, nhung canh theo "
                           f"{len(timed_cover_events)} moc thoi gian subtitle moi.")
    cover_meta = render_clean_video(
        raw_video, final_video, cover_mode,
        timed_cover_events or detected_events, log_cb,
        blur_padding_px=blur_padding_px,
        cover_offset_px=cover_offset_px,
        blur_power=blur_power,
        video_speed=video_speed,
    )
    return final_video, cover_meta, w, h


def step5_export(
    segs_vi: list,
    out_dir: Path,
    title: str,
    cover_meta: dict,
    w: int,
    h: int,
    cover_mode: str = "blur",
    subtitle_offset_sec: float = 0.0,
    subtitle_timing_scale: float = 1.0,
    video_speed: float = 1.0,
    subtitle_font_scale: float = 1.0,
    subtitle_font_size: int = 0,
    subtitle_margin_px: int = 0,
    srt_max_chars_per_line: int = 45,
    blur_padding_px: int = 12,
    blur_power: int = 4,
    cover_offset_px: int = 0,
    log_cb: Optional[Callable] = None,
) -> tuple[Optional[Path], list]:
    """Export SRT, script, bilingual files. Returns (srt_path, dub_segments)."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 5: XUAT FILE OUTPUT\n{'='*52}")
    srt_path = None
    dub_segments = list(segs_vi) if segs_vi else []
    if segs_vi:
        srt_path = out_dir / "file_sub_viet.srt"
        write_srt(segs_vi, srt_path, max_chars_per_line=srt_max_chars_per_line)
        _log_safe(log_cb, f"✓  Exported: {srt_path.name}")
        parsed_segments = parse_srt(srt_path)
        if parsed_segments:
            dub_segments = parsed_segments
        render_meta_path = out_dir / "render_meta.json"
        render_meta_path.write_text(
            json.dumps({
                "cover_mode": cover_mode,
                "video_width": w,
                "video_height": h,
                "subtitle_top_y": cover_meta.get("subtitle_top_y"),
                "subtitle_bottom_y": cover_meta.get("subtitle_bottom_y"),
                "cover_top_y": cover_meta.get("cover_top_y"),
                "cover_bottom_y": cover_meta.get("cover_bottom_y"),
                "cover_offset_px": cover_offset_px,
                "subtitle_offset_sec": subtitle_offset_sec,
                "subtitle_timing_scale": subtitle_timing_scale,
                "video_speed": video_speed,
                "subtitle_font_scale": subtitle_font_scale,
                "subtitle_font_size": subtitle_font_size,
                "subtitle_margin_px": subtitle_margin_px,
                "srt_max_chars_per_line": srt_max_chars_per_line,
                "blur_padding_px": blur_padding_px,
                "blur_power": blur_power,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _log_safe(log_cb, f"✓  Exported: {render_meta_path.name}")
        script_path = out_dir / "kich_ban_dich.txt"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(f"KICH BAN DICH: {title}\n{'='*60}\n\n")
            for seg in segs_vi:
                f.write(f"{seg['text']}\n")
        _log_safe(log_cb, f"✓  Exported: {script_path.name}")
        bilingual_path = out_dir / "song_ngu_tham_chieu.txt"
        with open(bilingual_path, "w", encoding="utf-8") as f:
            f.write(f"SONG NGU THAM CHIEU: {title}\n{'='*60}\n\n")
            for seg in segs_vi:
                if "original" in seg:
                    f.write(f"[CN] {seg['original']}\n")
                f.write(f"[VI] {seg['text']}\n\n")
        _log_safe(log_cb, f"✓  Exported: {bilingual_path.name}")
    return srt_path, dub_segments
```

- [ ] **Step 4: Thêm `step6_burn_sub` và `step7_dub` vào workflow.py**

```python
def step6_burn_sub(
    final_video: Path,
    srt_path: Path,
    cover_meta: dict,
    out_dir: Path,
    subtitle_font_scale: float = 1.0,
    subtitle_font_size: int = 0,
    subtitle_margin_px: int = 0,
    log_cb: Optional[Callable] = None,
) -> Path:
    """Burn subtitles into video. Returns path to burned video."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 6: GHI PHU DE TV VAO VIDEO\n{'='*52}")
    burned = out_dir / "video_sub_viet.mp4"
    burn_subtitle(
        final_video, srt_path, burned,
        cover_meta.get("subtitle_top_y"),
        cover_meta.get("subtitle_bottom_y"),
        log_cb,
        font_scale=subtitle_font_scale,
        font_size_override=subtitle_font_size,
        margin_offset=subtitle_margin_px,
    )
    return burned if burned.exists() else final_video


def step7_dub(
    video_source: Path,
    dub_segments: list,
    out_dir: Path,
    dub_mode: str = "preset",
    dub_backend_mode: str = "turbo",
    dub_remote_api_base: str = "http://localhost:23333/v1",
    dub_preset_voice: str = "",
    dub_ref_audio: str = "",
    dub_ref_text: str = "",
    dub_voice_volume: float = 1.35,
    dub_source_volume: float = 0.18,
    dub_mix_mode: str = "nen_nho",
    burn_sub: bool = False,
    log_cb: Optional[Callable] = None,
) -> None:
    """Render dubbed audio/video outputs."""
    _log_safe(log_cb, f"\n{'='*52}\n  BUOC 7: LONG TIENG TIENG VIET\n{'='*52}")
    output_video_name = ("video_sub_viet_long_tieng.mp4" if burn_sub
                         else "video_long_tieng.mp4")
    dubbed = render_dubbed_outputs(
        video_source, dub_segments, out_dir,
        mode=dub_mode,
        engine_mode=dub_backend_mode,
        remote_api_base=dub_remote_api_base,
        preset_voice=dub_preset_voice,
        ref_audio=dub_ref_audio,
        ref_text=dub_ref_text,
        dub_volume=dub_voice_volume,
        source_volume=dub_source_volume,
        mix_mode=dub_mix_mode,
        output_video_name=output_video_name,
        log_cb=log_cb,
    )
    _log_safe(log_cb, f"✓  Exported: {dubbed['dub_track'].name}")
    _log_safe(log_cb, f"✓  Exported: {dubbed['dub_video'].name}")
```

- [ ] **Step 5: Refactor `process_video` để gọi 7 hàm step**

Thay toàn bộ body của `process_video` (từ dòng `try:` đến `finally:`) bằng:

```python
    temp_dir = Path(config.get("output_base_dir", "output")) / "_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_dir = None

    try:
        raw_video, raw_audio, title, out_dir = step1_download(source_input, temp_dir, log_cb)

        segs = step2_transcribe(out_dir, log_cb)

        segs_vi = step3_translate(
            segs,
            subtitle_offset_sec=subtitle_offset_sec,
            subtitle_timing_scale=subtitle_timing_scale,
            video_speed=video_speed,
            log_cb=log_cb,
        )

        final_video, cover_meta, w, h = step4_cover(
            raw_video, segs_vi, out_dir,
            cover_mode=cover_mode,
            blur_padding_px=blur_padding_px,
            cover_offset_px=cover_offset_px,
            blur_power=blur_power,
            video_speed=video_speed,
            log_cb=log_cb,
        )

        srt_path, dub_segments = step5_export(
            segs_vi, out_dir, title, cover_meta, w, h,
            cover_mode=cover_mode,
            subtitle_offset_sec=subtitle_offset_sec,
            subtitle_timing_scale=subtitle_timing_scale,
            video_speed=video_speed,
            subtitle_font_scale=subtitle_font_scale,
            subtitle_font_size=subtitle_font_size,
            subtitle_margin_px=subtitle_margin_px,
            srt_max_chars_per_line=srt_max_chars_per_line,
            blur_padding_px=blur_padding_px,
            blur_power=blur_power,
            cover_offset_px=cover_offset_px,
            log_cb=log_cb,
        )

        dub_video_source = final_video
        if burn_sub and segs_vi and srt_path:
            dub_video_source = step6_burn_sub(
                final_video, srt_path, cover_meta, out_dir,
                subtitle_font_scale=subtitle_font_scale,
                subtitle_font_size=subtitle_font_size,
                subtitle_margin_px=subtitle_margin_px,
                log_cb=log_cb,
            )

        if enable_dub and dub_segments:
            step7_dub(
                dub_video_source, dub_segments, out_dir,
                dub_mode=dub_mode,
                dub_backend_mode=dub_backend_mode,
                dub_remote_api_base=dub_remote_api_base,
                dub_preset_voice=dub_preset_voice,
                dub_ref_audio=dub_ref_audio,
                dub_ref_text=dub_ref_text,
                dub_voice_volume=dub_voice_volume,
                dub_source_volume=dub_source_volume,
                dub_mix_mode=dub_mix_mode,
                burn_sub=burn_sub,
                log_cb=log_cb,
            )

        # Summary
        _log_safe(log_cb, "\n" + "="*52)
        _log_safe(log_cb, "  HOAN TAT!")
        for f in sorted(out_dir.iterdir()):
            icon = {".mp4": "🎥", ".mp3": "🎵", ".srt": "📝", ".txt": "📄"}.get(f.suffix, "📁")
            mb = f.stat().st_size / 1024 / 1024
            _log_safe(log_cb, f"  {icon}  {f.name:<38} {mb:6.1f} MB")
        _log_safe(log_cb, "="*52)

        return str(out_dir.resolve())

    except Exception as e:
        _log_safe(log_cb, f"\n❌  LOI: {str(e)}")
        import traceback
        _log_safe(log_cb, traceback.format_exc())
        return None

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 6: Cập nhật import trong `workflow.py` — xóa `statistics` ở top-level (đã move vào helper)**

Xóa dòng `import statistics` ở đầu file (dòng 5), vì đã được import trong `_retime_cover_events`.

- [ ] **Step 7: Khởi động app kiểm tra không có lỗi import**

```bash
cd C:\Users\xhiep\Downloads\dubbing-extractor
venv\Scripts\python.exe -c "from src.modules.workflow import process_video, step1_download, step2_transcribe, step3_translate, step4_cover, step5_export, step6_burn_sub, step7_dub; print('OK')"
```

Expected: `OK`

---

### Task 2: Xóa `quick_dub_toggle` duplicate trong `main.py`

**Files:**
- Modify: `main.py:196-209`

- [ ] **Step 1: Xóa block quick_dub_toggle (dòng 196-209)**

Tìm và xóa đoạn code sau trong `main.py`:

```python
    quick_dub_frame = tk.Frame(action_frame, bg='#f5f5f5')
    quick_dub_frame.pack(side=tk.LEFT, padx=(15, 0))
    quick_dub_toggle = tk.Checkbutton(
        quick_dub_frame,
        text="🎙 Lồng Tiếng",
        variable=enable_dub_state.var,
        onvalue=True,
        offvalue=False,
        font=("Segoe UI", 11, "bold"),
        bg='#f5f5f5',
        activebackground='#f5f5f5',
        selectcolor='#3498db'
    )
    quick_dub_toggle.pack()
```

Thay bằng: *(không có gì — xóa hoàn toàn đoạn này)*

- [ ] **Step 2: Kiểm tra app khởi động không lỗi**

```bash
cd C:\Users\xhiep\Downloads\dubbing-extractor
venv\Scripts\python.exe -c "import main; print('OK')"
```

Expected: `OK`

---

### Task 3: Thêm `pipeline_state` và 5 nút Bước trong tab Nguồn

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Thêm import step functions vào đầu main.py**

Sau dòng `from src.modules.workflow import process_video` (dòng 23), thêm:

```python
from src.modules.workflow import (
    process_video,
    step1_download,
    step2_transcribe,
    step3_translate,
    step4_cover,
    step5_export,
)
```

*(Thay dòng import cũ `from src.modules.workflow import process_video`)*

- [ ] **Step 2: Thêm `pipeline_state` dict sau phần khai báo state variables**

Sau dòng `tts_preview_text_state = use_tk_state(...)` (khoảng dòng 172), thêm:

```python
    # Pipeline state — lưu kết quả giữa các bước
    pipeline_state: dict = {
        "temp_dir": None,      # Path: thư mục temp
        "raw_video": None,     # Path: video đã tải/local
        "raw_audio": None,     # Path: audio gốc
        "title": None,         # str: tên video
        "out_dir": None,       # Path: thư mục output
        "segs": None,          # list: segments từ whisper
        "segs_vi": None,       # list: segments đã dịch
        "final_video": None,   # Path: video đã xử lý cover
        "cover_meta": None,    # dict: metadata vùng che
        "video_w": None,       # int
        "video_h": None,       # int
        "srt_path": None,      # Path: file SRT tiếng Việt
        "dub_segments": None,  # list: segments cho TTS
        "last_step": 0,        # int: bước cuối đã xong
    }
```

- [ ] **Step 3: Thêm card "Chạy Từng Bước" vào tab Nguồn sau source_card**

Sau dòng `source_card.pack(fill=tk.X, pady=5)` (dòng 298), thêm:

```python
    # Step-by-step pipeline card
    steps_card = Card(source_tab, title="🔢 Chạy Từng Bước")
    steps_container = steps_card.get_container()

    step_hint = tk.Label(
        steps_container,
        text="Bấm Bước N = chạy từ đầu đến hết bước N. Sau Bước 3 có thể sửa SRT trước khi chạy Bước 4.",
        font=("Segoe UI", 9),
        fg="#7f8c8d",
        anchor="w",
        justify=tk.LEFT,
        wraplength=600,
    )
    step_hint.pack(anchor=tk.W, pady=(0, 8))

    step_btn_row = tk.Frame(steps_container, bg="white")
    step_btn_row.pack(anchor=tk.W, pady=(0, 4))

    step1_btn = tk.Button(step_btn_row, text="Bước 1\nTải Video", width=10, height=2,
                          bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                          command=lambda: run_up_to_step(1))
    step1_btn.pack(side=tk.LEFT, padx=(0, 4))

    step2_btn = tk.Button(step_btn_row, text="Bước 2\nWhisper", width=10, height=2,
                          bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                          command=lambda: run_up_to_step(2))
    step2_btn.pack(side=tk.LEFT, padx=(0, 4))

    step3_btn = tk.Button(step_btn_row, text="Bước 3\nDịch", width=10, height=2,
                          bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                          command=lambda: run_up_to_step(3))
    step3_btn.pack(side=tk.LEFT, padx=(0, 4))

    step4_btn = tk.Button(step_btn_row, text="Bước 4\nChe Sub", width=10, height=2,
                          bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                          command=lambda: run_up_to_step(4))
    step4_btn.pack(side=tk.LEFT, padx=(0, 4))

    step5_btn = tk.Button(step_btn_row, text="Bước 5\nXuất File", width=10, height=2,
                          bg="#1565C0", fg="white", font=("Segoe UI", 9, "bold"),
                          command=lambda: run_up_to_step(5))
    step5_btn.pack(side=tk.LEFT, padx=(0, 4))

    step_status_var = tk.StringVar(value="")
    step_status_label = tk.Label(steps_container, textvariable=step_status_var,
                                 anchor="w", fg="#333", font=("Segoe UI", 9))
    step_status_label.pack(anchor=tk.W, pady=(4, 0))

    # SRT editor — hiện sau Bước 3
    srt_editor_frame = tk.Frame(steps_container, bg="white")
    # (KHÔNG pack ngay — sẽ pack/forget tùy bước)

    srt_editor_label = tk.Label(srt_editor_frame,
                                text="✏️ SRT sau dịch — có thể sửa trước khi chạy Bước 4:",
                                anchor="w", font=("Segoe UI", 9, "bold"))
    srt_editor_label.pack(anchor=tk.W, pady=(8, 2))

    srt_editor_box = tk.Text(srt_editor_frame, height=12, font=("Consolas", 9),
                             wrap=tk.NONE, undo=True)
    srt_editor_scroll_y = ttk.Scrollbar(srt_editor_frame, orient=tk.VERTICAL,
                                         command=srt_editor_box.yview)
    srt_editor_scroll_x = ttk.Scrollbar(srt_editor_frame, orient=tk.HORIZONTAL,
                                         command=srt_editor_box.xview)
    srt_editor_box.configure(yscrollcommand=srt_editor_scroll_y.set,
                              xscrollcommand=srt_editor_scroll_x.set)
    srt_editor_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    srt_editor_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    srt_editor_box.pack(fill=tk.BOTH, expand=True)

    srt_editor_btn_row = tk.Frame(srt_editor_frame, bg="white")
    srt_editor_btn_row.pack(anchor=tk.W, pady=(4, 0))

    srt_open_btn = tk.Button(srt_editor_btn_row, text="📂 Mở File SRT Ngoài",
                             command=lambda: open_srt_in_editor())
    srt_open_btn.pack(side=tk.LEFT, padx=(0, 8))

    srt_save_btn = tk.Button(srt_editor_btn_row, text="💾 Lưu Thay Đổi SRT",
                             bg="#27ae60", fg="white",
                             command=lambda: save_srt_edits())
    srt_save_btn.pack(side=tk.LEFT)

    srt_save_status_var = tk.StringVar(value="")
    tk.Label(srt_editor_btn_row, textvariable=srt_save_status_var,
             fg="#275", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)

    steps_card.pack(fill=tk.X, pady=5)
```

- [ ] **Step 4: Xác minh UI khởi động không lỗi**

```bash
cd C:\Users\xhiep\Downloads\dubbing-extractor
venv\Scripts\python.exe -c "import main; print('UI structure OK')"
```

Expected: `UI structure OK`

---

### Task 4: Implement hàm `run_up_to_step` và các helper SRT

**Files:**
- Modify: `main.py` — thêm các hàm vào phần helper functions (sau hàm `log`)

- [ ] **Step 1: Thêm hàm `_show_srt_editor` và `_hide_srt_editor`**

Thêm sau hàm `log` (khoảng dòng 641):

```python
    def _show_srt_editor():
        """Hiện ô edit SRT và load nội dung từ pipeline_state['srt_path']."""
        srt_path = pipeline_state.get("srt_path")
        srt_editor_box.delete("1.0", tk.END)
        if srt_path and Path(srt_path).exists():
            content = Path(srt_path).read_text(encoding="utf-8")
            srt_editor_box.insert("1.0", content)
        srt_editor_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        srt_save_status_var.set("")

    def _hide_srt_editor():
        srt_editor_frame.pack_forget()

    def open_srt_in_editor():
        srt_path = pipeline_state.get("srt_path")
        if not srt_path or not Path(srt_path).exists():
            srt_save_status_var.set("Chưa có file SRT.")
            return
        try:
            subprocess.Popen(["notepad.exe", str(srt_path)])
        except Exception as exc:
            srt_save_status_var.set(f"Không mở được: {exc}")

    def save_srt_edits():
        srt_path = pipeline_state.get("srt_path")
        if not srt_path:
            srt_save_status_var.set("Chưa có file SRT để lưu.")
            return
        content = srt_editor_box.get("1.0", tk.END)
        try:
            Path(srt_path).write_text(content, encoding="utf-8")
            srt_save_status_var.set(f"✓ Đã lưu lúc {datetime.now().strftime('%H:%M:%S')}")
        except Exception as exc:
            srt_save_status_var.set(f"Lỗi lưu: {exc}")
```

- [ ] **Step 2: Thêm hàm `_reset_pipeline_temp`**

```python
    def _reset_pipeline_temp():
        """Xóa temp dir cũ nếu có."""
        old_temp = pipeline_state.get("temp_dir")
        if old_temp and Path(old_temp).exists():
            import shutil as _shutil
            _shutil.rmtree(old_temp, ignore_errors=True)
```

- [ ] **Step 3: Thêm hàm `_collect_params` để gom params từ UI state**

```python
    def _collect_params() -> dict:
        """Gom tất cả params từ UI state thành dict."""
        return {
            "cover_mode": cover_mode_state.get(),
            "subtitle_offset_sec": float(subtitle_offset_state.get()),
            "subtitle_timing_scale": float(subtitle_scale_state.get()),
            "video_speed": float(video_speed_state.get()),
            "subtitle_font_scale": float(font_scale_state.get()),
            "subtitle_font_size": int(font_size_state.get()),
            "subtitle_margin_px": int(margin_state.get()),
            "srt_max_chars_per_line": int(chars_per_line_state.get()),
            "blur_padding_px": int(blur_padding_state.get()),
            "cover_offset_px": int(cover_offset_state.get()),
            "blur_power": int(blur_power_state.get()),
        }
```

- [ ] **Step 4: Thêm hàm `run_up_to_step`**

```python
    def run_up_to_step(target_step: int):
        """Chạy pipeline từ đầu đến bước target_step."""
        from pathlib import Path as _Path
        import shutil as _shutil
        from src.modules.workflow import (
            step1_download, step2_transcribe, step3_translate,
            step4_cover, step5_export,
        )
        from src.config import config as _config

        source = source_state.get().strip()
        if not source:
            step_status_var.set("❌ Vui lòng nhập link video hoặc đường dẫn file.")
            return

        # Cập nhật whisper model vào config trước khi chạy
        _config["whisper_model"] = whisper_model_state.get()
        _config["video_speed"] = float(video_speed_state.get())
        _config["blur_padding_px"] = int(blur_padding_state.get())
        _config["cover_offset_px"] = int(cover_offset_state.get())
        _config["blur_power"] = int(blur_power_state.get())

        params = _collect_params()

        # Vô hiệu hóa tất cả nút step
        all_step_btns = [step1_btn, step2_btn, step3_btn, step4_btn, step5_btn, start_btn]
        for btn in all_step_btns:
            btn.config(state=tk.DISABLED)
        _hide_srt_editor()

        try:
            # Reset pipeline state
            _reset_pipeline_temp()
            pipeline_state.update({
                "temp_dir": None, "raw_video": None, "raw_audio": None,
                "title": None, "out_dir": None, "segs": None, "segs_vi": None,
                "final_video": None, "cover_meta": None, "video_w": None,
                "video_h": None, "srt_path": None, "dub_segments": None,
                "last_step": 0,
            })

            # ── Bước 1 ──────────────────────────────────────────────────────
            step_status_var.set("⏳ Đang chạy Bước 1 (Tải video)...")
            root.update()
            temp_dir = _Path(_config.get("output_base_dir", "output")) / "_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            pipeline_state["temp_dir"] = str(temp_dir)
            raw_video, raw_audio, title, out_dir = step1_download(source, temp_dir, log)
            pipeline_state.update({
                "raw_video": str(raw_video),
                "raw_audio": str(raw_audio),
                "title": title,
                "out_dir": str(out_dir),
                "last_step": 1,
            })
            step_status_var.set(f"✓ Bước 1 xong → {out_dir.name}")
            if target_step == 1:
                return

            # ── Bước 2 ──────────────────────────────────────────────────────
            step_status_var.set("⏳ Đang chạy Bước 2 (Whisper)...")
            root.update()
            segs = step2_transcribe(out_dir, log)
            pipeline_state["segs"] = segs
            pipeline_state["last_step"] = 2
            step_status_var.set(f"✓ Bước 2 xong → {len(segs)} đoạn")
            if target_step == 2:
                return

            # ── Bước 3 ──────────────────────────────────────────────────────
            step_status_var.set("⏳ Đang chạy Bước 3 (Dịch)...")
            root.update()
            segs_vi = step3_translate(
                segs,
                subtitle_offset_sec=params["subtitle_offset_sec"],
                subtitle_timing_scale=params["subtitle_timing_scale"],
                video_speed=params["video_speed"],
                log_cb=log,
            )
            pipeline_state["segs_vi"] = segs_vi
            pipeline_state["last_step"] = 3

            # Lưu SRT tạm để user có thể edit
            if segs_vi:
                from src.modules.transcription.srt_generator import write_srt
                temp_srt = out_dir / "file_sub_viet.srt"
                write_srt(segs_vi, temp_srt,
                          max_chars_per_line=params["srt_max_chars_per_line"])
                pipeline_state["srt_path"] = str(temp_srt)

            step_status_var.set(f"✓ Bước 3 xong → {len(segs_vi)} đoạn dịch. Có thể sửa SRT bên dưới.")
            _show_srt_editor()
            notebook.select(source_tab)
            if target_step == 3:
                return

            # ── Bước 4 ──────────────────────────────────────────────────────
            step_status_var.set("⏳ Đang chạy Bước 4 (Che sub gốc)...")
            root.update()
            # Nếu user đã sửa SRT và lưu, reload segs_vi từ SRT đã lưu
            srt_path_str = pipeline_state.get("srt_path")
            if srt_path_str and _Path(srt_path_str).exists():
                from src.modules.transcription.srt_generator import parse_srt
                reloaded = parse_srt(_Path(srt_path_str))
                if reloaded:
                    segs_vi = reloaded
                    pipeline_state["segs_vi"] = segs_vi

            final_video, cover_meta, w, h = step4_cover(
                _Path(pipeline_state["raw_video"]),
                segs_vi,
                out_dir,
                cover_mode=params["cover_mode"],
                blur_padding_px=params["blur_padding_px"],
                cover_offset_px=params["cover_offset_px"],
                blur_power=params["blur_power"],
                video_speed=params["video_speed"],
                log_cb=log,
            )
            pipeline_state.update({
                "final_video": str(final_video),
                "cover_meta": cover_meta,
                "video_w": w,
                "video_h": h,
                "last_step": 4,
            })
            step_status_var.set("✓ Bước 4 xong → video_ready.mp4")
            if target_step == 4:
                return

            # ── Bước 5 ──────────────────────────────────────────────────────
            step_status_var.set("⏳ Đang chạy Bước 5 (Xuất file)...")
            root.update()
            srt_path, dub_segments = step5_export(
                segs_vi, out_dir, pipeline_state["title"],
                cover_meta, w, h,
                **{k: params[k] for k in [
                    "cover_mode", "subtitle_offset_sec", "subtitle_timing_scale",
                    "video_speed", "subtitle_font_scale", "subtitle_font_size",
                    "subtitle_margin_px", "srt_max_chars_per_line",
                    "blur_padding_px", "blur_power", "cover_offset_px",
                ]},
                log_cb=log,
            )
            pipeline_state.update({
                "srt_path": str(srt_path) if srt_path else None,
                "dub_segments": dub_segments,
                "last_step": 5,
            })
            save_app_config({"last_render_dir": str(out_dir)})
            last_output_var.set(str(out_dir))
            load_preview_segments(str(out_dir))
            step_status_var.set(f"✓ Tất cả {target_step} bước hoàn tất → {out_dir.name}")
            notebook.select(adjust_tab)

        except Exception as exc:
            import traceback
            step_status_var.set(f"❌ Lỗi bước {pipeline_state.get('last_step', 0)+1}: {exc}")
            log(f"[ERROR] {exc}")
            log(traceback.format_exc())
            notebook.select(log_tab)

        finally:
            for btn in all_step_btns:
                btn.config(state=tk.NORMAL)
            # Cleanup temp
            _reset_pipeline_temp()
```

- [ ] **Step 5: Thêm import `datetime` vào `save_srt_edits` (nếu chưa có)**

Kiểm tra dòng đầu `main.py` xem `from datetime import datetime` đã có chưa. Nếu chưa, thêm vào sau `import subprocess`:

```python
from datetime import datetime
```

- [ ] **Step 6: Xác minh chạy được**

```bash
cd C:\Users\xhiep\Downloads\dubbing-extractor
venv\Scripts\python.exe -c "import main; print('All functions OK')"
```

Expected: `All functions OK`

---

### Task 5: Kiểm thử tích hợp thủ công

**Files:** không có file mới

- [ ] **Step 1: Chạy app, bấm Bước 1 với file local `test.mp4`**

```bash
cd C:\Users\xhiep\Downloads\dubbing-extractor
venv\Scripts\python.exe main.py
```

Trong UI:
1. Dán đường dẫn `C:\Users\xhiep\Downloads\dubbing-extractor\test.mp4` vào ô Nguồn
2. Bấm **"Bước 1\nTải Video"**
3. Xác nhận: nhật ký hiện "BUOC 1", status bar hiện "✓ Bước 1 xong", không có lỗi

- [ ] **Step 2: Bấm Bước 3 — xác nhận SRT editor hiện ra**

1. Bấm **"Bước 3\nDịch"**
2. Xác nhận: sau khi xong, ô SRT editor hiện trong tab Nguồn, có nội dung SRT tiếng Việt
3. Sửa 1 dòng SRT trong ô edit
4. Bấm **"💾 Lưu Thay Đổi SRT"** → hiện "✓ Đã lưu lúc HH:MM:SS"

- [ ] **Step 3: Bấm Bước 5 — xác nhận pipeline hoàn tất**

1. Bấm **"Bước 5\nXuất File"**
2. Xác nhận: sau khi xong, chuyển sang tab Căn Chỉnh, `last_output_var` có giá trị, file `file_sub_viet.srt` tồn tại trong output dir
3. Xác nhận nút "Bắt Đầu Xử Lý" đầy đủ pipeline vẫn hoạt động bình thường

- [ ] **Step 4: Xác nhận checkbox "Lồng Tiếng" trong toolbar đã bị xóa**

Nhìn vào action bar phía trên: chỉ còn 2 nút (▶ Bắt Đầu Xử Lý, 🗑 Xóa Nhật Ký), không còn checkbox "🎙 Lồng Tiếng" nữa.

---

## Lưu ý khi thực thi

- **Thứ tự Task:** Task 1 → Task 2 → Task 3 → Task 4 → Task 5
- **Task 3 & 4 phụ thuộc vào Task 1** (step functions phải có trước khi import vào main.py)
- Mỗi Task xong, kiểm tra `python -c "import ..."` trước khi tiếp tục
- Nếu app không khởi động được, kiểm tra console error — thường là lỗi tên hàm không khớp
