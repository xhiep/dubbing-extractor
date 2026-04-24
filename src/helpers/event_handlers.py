"""UI event handlers and callbacks."""
import os
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import winsound

from src.modules.tts import (
    is_vieneu_available,
    list_preset_voices,
    release_tts_resources,
    synthesize_speech,
)
from src.modules.downloader.ytdlp_wrapper import fetch_preview_info
from src.modules.video_processing.ffmpeg_wrapper import get_dims, probe_duration
from src.utils.file_utils import is_local_file
from src.helpers.preview_helpers import (
    extract_local_preview_frame,
    extract_remote_preview_frame,
)


class UIEventHandlers:
    """Manages UI event handlers and callbacks."""

    def __init__(self, root, output_dir: Path):
        self.root = root
        self.output_dir = output_dir

    def paste_clipboard(self, source_state, load_preview_fn):
        """Paste from clipboard to source input."""
        try:
            source_state.set(self.root.clipboard_get().strip())
            load_preview_fn(force=True)
        except:
            pass

    def browse_file(self, source_state, load_preview_fn):
        """Browse for video file."""
        filename = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[("File video", "*.mp4 *.avi *.mkv *.mov *.flv"), ("Tất cả file", "*.*")]
        )
        if filename:
            source_state.set(filename)
            load_preview_fn(force=True)

    def browse_ref_audio(self, dub_ref_audio_state):
        """Browse for reference audio file."""
        filename = filedialog.askopenfilename(
            title="Chọn file audio mẫu",
            filetypes=[("File audio", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg"), ("Tất cả file", "*.*")]
        )
        if filename:
            dub_ref_audio_state.set(filename)

    def open_srt_external(self, pipeline_state, status_setter):
        """Open SRT file in external editor."""
        srt_path = pipeline_state.get("srt_path")
        if srt_path and Path(srt_path).exists():
            os.startfile(srt_path)
        else:
            status_setter("⚠ Chưa có file SRT để mở.", "#e67e22")

    def reload_srt_from_file(self, pipeline_state, enable_srt_fn, status_setter):
        """Reload SRT content from file."""
        srt_path = pipeline_state.get("srt_path")
        if srt_path and Path(srt_path).exists():
            enable_srt_fn(srt_path)
            status_setter("✓ Đã tải lại nội dung SRT từ file.", "#27ae60")
        else:
            status_setter("⚠ Chưa có file SRT để tải lại.", "#e67e22")

    def save_srt_to_file(self, pipeline_state, srt_editor, status_setter):
        """Save SRT editor content to file."""
        srt_path = pipeline_state.get("srt_path")
        if not srt_path:
            status_setter("⚠ Chưa có file SRT để lưu.", "#e67e22")
            return
        content = srt_editor.get("1.0", tk.END)
        try:
            Path(srt_path).write_text(content, encoding="utf-8")
            status_setter(f"✓ Đã lưu thay đổi vào {Path(srt_path).name}", "#27ae60")
        except Exception as exc:
            status_setter(f"❌ Lưu file SRT thất bại: {exc}", "#e74c3c")

    def open_render_folder(self, last_output_var, preview_status_var):
        """Open render output folder in explorer."""
        render_dir = last_output_var.get().strip()
        if not render_dir:
            preview_status_var.set("Chưa có thư mục render để mở.")
            return
        render_path = Path(render_dir)
        if not render_path.exists():
            preview_status_var.set("Thư mục render hiện không tồn tại.")
            return
        try:
            subprocess.Popen(["explorer.exe", str(render_path)])
            preview_status_var.set(f"Đã mở thư mục render: {render_path.name}")
        except Exception as exc:
            preview_status_var.set(f"Mở thư mục render thất bại: {exc}")


class TTSEventHandlers:
    """Manages TTS-related event handlers."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.preview_path = output_dir / "_preview_cache" / "tts_preview.wav"

    def refresh_voice_list(
        self,
        backend_mode: str,
        remote_api_base: str,
        preset_voice_combo,
        dub_preset_voice_state,
        voice_guard: dict,
        status_setter,
    ):
        """Refresh available voice list."""
        if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
            from src.modules.tts import get_vieneu_error
            status_setter(
                f"VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}",
                "#a33",
            )
            preset_voice_combo.configure(values=[])
            return
        try:
            voices = list_preset_voices(engine_mode=backend_mode, remote_api_base=remote_api_base)
            voice_guard["options"] = voices
            preset_voice_combo.configure(values=voices)
            if voices and not dub_preset_voice_state.get():
                dub_preset_voice_state.set(voices[0])
            status_setter(f"VieNeu-TTS sẵn sàng | mode={backend_mode} | {len(voices)} giọng mẫu", "#275")
        except Exception as exc:
            status_setter(f"Tải danh sách giọng thất bại: {exc}", "#a33")
        finally:
            release_tts_resources()

    def sync_dub_mode(
        self,
        dub_mode: str,
        backend_mode: str,
        preset_voice_combo,
        dub_refresh_voice_btn,
        ref_audio_entry,
        dub_browse_ref_btn,
        ref_text_box,
        dub_remote_entry,
    ):
        """Sync UI state based on dub mode."""
        preset_enabled = dub_mode == "preset"
        clone_enabled = dub_mode == "clone"
        remote_enabled = backend_mode == "remote"
        preset_voice_combo.configure(state="readonly" if preset_enabled else "disabled")
        dub_refresh_voice_btn.configure(state=tk.NORMAL if preset_enabled else tk.DISABLED)
        ref_audio_entry.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        dub_browse_ref_btn.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        ref_text_box.configure(state=tk.NORMAL if clone_enabled else tk.DISABLED)
        dub_remote_entry.configure(state=tk.NORMAL if remote_enabled else tk.DISABLED)

    def stop_preview_audio(self):
        """Stop audio preview playback."""
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def play_tts_preview(
        self,
        backend_mode: str,
        remote_api_base: str,
        dub_mode: str,
        preset_voice: str,
        ref_audio: str,
        tts_preview_text: str,
        ref_text: str,
        status_setter,
        log_fn,
    ):
        """Play TTS preview."""
        self.stop_preview_audio()
        if not is_vieneu_available(engine_mode=backend_mode, remote_api_base=remote_api_base):
            from src.modules.tts import get_vieneu_error
            status_setter(
                f"VieNeu-TTS chưa sẵn sàng: {get_vieneu_error(engine_mode=backend_mode, remote_api_base=remote_api_base)}",
                "#a33",
            )
            return
        try:
            self.preview_path.parent.mkdir(parents=True, exist_ok=True)
            synthesize_speech(
                text=tts_preview_text,
                out_path=self.preview_path,
                mode=dub_mode,
                engine_mode=backend_mode,
                remote_api_base=remote_api_base,
                preset_voice=preset_voice,
                ref_audio=ref_audio,
                ref_text=ref_text,
                log_cb=log_fn,
            )
            winsound.PlaySound(str(self.preview_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            status_setter(f"Đã tạo và phát mẫu nghe thử | mode={backend_mode}", "#275")
        except Exception as exc:
            status_setter(f"Nghe thử thất bại: {exc}", "#a33")
        finally:
            release_tts_resources()


class PreviewEventHandlers:
    """Manages preview-related event handlers."""

    def __init__(self, root, output_dir: Path):
        self.root = root
        self.output_dir = output_dir

    def load_source_preview(
        self,
        source: str,
        preview_guard: dict,
        preview_status_var,
        preview_seek,
        preview_time_state,
        render_frame_fn,
        update_time_label_fn,
        render_markers_fn,
        stop_playback_fn,
        force: bool = False,
    ):
        """Load preview from source (local file or remote URL)."""
        if not source:
            preview_status_var.set("Chưa tải xem trước.")
            preview_guard["image"] = None
            preview_guard["kind"] = None
            preview_guard["source"] = None
            preview_guard["duration"] = 0.0
            preview_guard["path"] = None
            preview_guard["segments"] = []
            preview_seek.config(state=tk.DISABLED, to=100)
            preview_seek.set(0)
            update_time_label_fn()
            render_markers_fn()
            stop_playback_fn()
            return
        if not force and preview_guard["source"] == source:
            return

        stop_playback_fn()
        preview_status_var.set("Đang tải preview...")
        self.root.update_idletasks()
        try:
            if is_local_file(source):
                dims = get_dims(Path(source))
                duration = probe_duration(Path(source))
                preview_guard["kind"] = "local"
                preview_guard["duration"] = duration
                preview_guard["path"] = source
                preview_seek.config(state=tk.NORMAL, from_=0, to=max(duration, 0.1))
                render_frame_fn(min(1.0, duration))
                from src.helpers.preview_helpers import format_duration
                preview_status_var.set(
                    f"Xem trước file local | {format_duration(duration)} | {dims[0]}x{dims[1]} | {Path(source).name}"
                )
            else:
                info = fetch_preview_info(source)
                thumb = info.get("thumbnail")
                preview_guard["kind"] = "remote"
                preview_guard["duration"] = float(info.get("duration", 0) or 0)
                preview_guard["path"] = None
                preview_seek.config(state=tk.DISABLED, from_=0, to=max(preview_guard["duration"], 0.1))
                preview_seek.set(0)
                preview_time_state.set(0.0)
                update_time_label_fn()
                if thumb:
                    preview_path = extract_remote_preview_frame(thumb, self.output_dir)
                    import tkinter as tk
                    photo = tk.PhotoImage(file=str(preview_path))
                    preview_guard["image"] = photo
                    preview_guard["live_render"] = False
                else:
                    preview_guard["image"] = None
                from src.helpers.preview_helpers import format_duration
                preview_status_var.set(
                    f"{info.get('title','video')} | {format_duration(info.get('duration', 0))} | "
                    f"{info.get('uploader','')} | {info.get('view_count', 0):,} lượt xem"
                )
        except Exception as exc:
            preview_guard["image"] = None
            preview_guard["kind"] = None
            preview_guard["duration"] = 0.0
            preview_guard["path"] = None
            preview_guard["segments"] = []
            preview_status_var.set(f"Tải preview thất bại: {exc}")
        finally:
            preview_guard["source"] = source
            render_markers_fn()
