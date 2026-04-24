"""Preview and rendering helper functions."""
import json
import subprocess
import tkinter as tk
from pathlib import Path
from typing import Optional

from src.modules.video_processing.ffmpeg_wrapper import ffmpeg_cmd, get_dims
from src.modules.video_processing.subtitle_burner import compute_subtitle_layout
from src.utils.ui_helpers import expand_band_from_center, shift_band


def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    total = int(seconds or 0)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def wrap_preview_text(text: str, max_chars: int) -> str:
    """Wrap preview text to max chars per line."""
    text = (text or "").strip()
    if not text:
        return "Dòng phụ đề mẫu số 1\nDòng phụ đề mẫu số 2"
    if "\n" in text:
        return text
    if len(text) <= max_chars:
        return text
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for word in words:
        next_len = current_len + len(word) + (1 if current else 0)
        if next_len <= max_chars:
            current.append(word)
            current_len = next_len
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines[:2])


def load_render_meta(output_dir: str) -> dict:
    """Load render metadata from output directory."""
    if not output_dir:
        return {}
    meta_path = Path(output_dir) / "render_meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def extract_local_preview_frame(video_path: str, timestamp: float, output_dir: Path) -> Path:
    """Extract a single frame from local video at timestamp."""
    preview_dir = output_dir / "_preview_cache"
    preview_dir.mkdir(parents=True, exist_ok=True)
    out_path = preview_dir / "local_preview.png"
    cmd = [
        ffmpeg_cmd(), "-y",
        "-ss", f"{max(0.0, timestamp):.2f}",
        "-i", video_path,
        "-frames:v", "1",
        "-update", "1",
        "-vf", "scale=480:-1",
        str(out_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return out_path


def write_preview_srt(text: str, output_dir: Path) -> Path:
    """Write preview subtitle text to temporary SRT file."""
    preview_dir = output_dir / "_preview_cache"
    preview_dir.mkdir(parents=True, exist_ok=True)
    srt_path = preview_dir / "preview_overlay.srt"
    safe_text = (text or "").strip() or " "
    srt_path.write_text(
        "1\n00:00:00,000 --> 23:59:59,000\n" + safe_text + "\n",
        encoding="utf-8",
    )
    return srt_path


def escape_sub_path(path: Path) -> str:
    """Escape subtitle path for ffmpeg filter."""
    return str(path).replace("\\", "\\\\").replace(":", "\\:")


def render_local_preview_composite(
    video_path: str,
    timestamp: float,
    output_dir: Path,
    render_meta: dict,
    font_scale: float,
    font_size: int,
    margin: int,
    preview_text: str,
    cover_mode: str,
    blur_padding: int,
    cover_offset: int,
    blur_power: int,
) -> Path:
    """Render local preview with subtitle overlay and cover effects."""
    preview_dir = output_dir / "_preview_cache"
    preview_dir.mkdir(parents=True, exist_ok=True)
    out_path = preview_dir / "local_preview_rendered.png"

    dims = get_dims(Path(video_path))
    src_w, src_h = dims
    meta_top_y = render_meta.get("subtitle_top_y")
    meta_bottom_y = render_meta.get("subtitle_bottom_y")

    layout = compute_subtitle_layout(
        src_h,
        meta_top_y,
        meta_bottom_y,
        font_scale=font_scale,
        font_size_override=font_size,
        margin_offset=margin,
    )

    srt_path = write_preview_srt(preview_text, output_dir)
    style = (
        f"FontName=Arial,"
        f"FontSize={layout['font_size']},"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"BackColour=&H60000000,"
        f"Bold=1,"
        f"Outline=2,"
        f"Shadow=1,"
        f"Alignment=2,"
        f"MarginV={layout['margin_v']}"
    )

    filter_parts = []
    current_label = "[0:v]"

    if cover_mode in ("blur", "blackbar"):
        cover_top_y = render_meta.get("cover_top_y")
        cover_bottom_y = render_meta.get("cover_bottom_y")
        if cover_top_y is not None and cover_bottom_y is not None:
            top_y, bottom_y = shift_band(int(cover_top_y), int(cover_bottom_y), src_h, cover_offset)
        elif meta_top_y is not None and meta_bottom_y is not None:
            top_y, bottom_y = expand_band_from_center(meta_top_y, meta_bottom_y, src_h, blur_padding)
            top_y, bottom_y = shift_band(top_y, bottom_y, src_h, cover_offset)
        else:
            approx_bottom = src_h - layout["margin_v"]
            approx_height = max(layout["font_size"] * 2 + 24, int(src_h * 0.10))
            top_y, bottom_y = expand_band_from_center(
                int(approx_bottom - approx_height),
                int(approx_bottom),
                src_h,
                blur_padding,
            )
            top_y, bottom_y = shift_band(top_y, bottom_y, src_h, cover_offset)
        band_h = max(2, bottom_y - top_y + 1)

        if cover_mode == "blur":
            power = max(1, min(10, blur_power))
            luma_r = min(25, max(1, (band_h - 1) // 2))
            chroma_r = min(25, max(1, (band_h // 2 - 1) // 2))
            filter_parts.append(f"{current_label}split=2[base][src]")
            filter_parts.append(
                f"[src]crop=iw:{band_h}:0:{top_y},"
                f"boxblur=luma_radius={luma_r}:luma_power={power}:"
                f"chroma_radius={chroma_r}:chroma_power={power}[blur]"
            )
            filter_parts.append(f"[base][blur]overlay=0:{top_y}[covered]")
            current_label = "[covered]"
        else:
            filter_parts.append(
                f"{current_label}drawbox=x=0:y={top_y}:w=iw:h={band_h}:color=black:t=fill[covered]"
            )
            current_label = "[covered]"

    filter_parts.append(
        f"{current_label}subtitles='{escape_sub_path(srt_path)}':force_style='{style}',scale=480:-1[out]"
    )

    cmd = [
        ffmpeg_cmd(), "-y",
        "-ss", f"{max(0.0, timestamp):.2f}",
        "-i", video_path,
        "-frames:v", "1",
        "-filter_complex", ";".join(filter_parts),
        "-map", "[out]",
        str(out_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return out_path


def extract_remote_preview_frame(image_url: str, output_dir: Path) -> Path:
    """Extract preview frame from remote image URL."""
    preview_dir = output_dir / "_preview_cache"
    preview_dir.mkdir(parents=True, exist_ok=True)
    out_path = preview_dir / "remote_preview.png"
    cmd = [
        ffmpeg_cmd(), "-y",
        "-i", image_url,
        "-frames:v", "1",
        "-update", "1",
        "-vf", "scale=480:-1",
        str(out_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return out_path


def parse_srt_segments(srt_path: Path) -> list[dict]:
    """Parse SRT file into list of segment dictionaries."""
    if not srt_path.exists():
        return []

    def parse_time(value: str) -> float:
        hh, mm, rest = value.split(":")
        ss, ms = rest.split(",")
        return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000

    content = srt_path.read_text(encoding="utf-8", errors="ignore").strip()
    blocks = [block.strip() for block in content.split("\n\n") if block.strip()]
    segments = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        start_text, end_text = [part.strip() for part in lines[1].split("-->")]
        segments.append({
            "start": parse_time(start_text),
            "end": parse_time(end_text),
            "text": "\n".join(lines[2:]),
        })
    return segments


def resolve_latest_srt_output(preferred_output_dir: str, output_root: Path) -> str:
    """Resolve the latest SRT output directory."""
    preferred = Path(preferred_output_dir) if preferred_output_dir else None
    if preferred and (preferred / "file_sub_viet.srt").exists():
        return str(preferred)

    if not output_root.exists():
        return ""

    candidates = [
        path for path in output_root.iterdir()
        if path.is_dir() and (path / "file_sub_viet.srt").exists()
    ]
    if not candidates:
        return ""
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return str(latest)
