#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dubbing Extractor - Auto Installer
Chay tu dong: tao venv, cai ffmpeg, cai pip packages, cai PyTorch CUDA
Khong can chay bat ky lenh thu cong nao.
"""
import os
import sys
import shutil
import zipfile
import subprocess
import urllib.request
from pathlib import Path

# ── Color support ────────────────────────────────────────────────────────────
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
except Exception:
    GREEN = YELLOW = RED = CYAN = BOLD = RESET = ""

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_DIR     = PROJECT_ROOT / "venv"
VENV_PYTHON  = VENV_DIR / "Scripts" / "python.exe"
VENV_PIP     = VENV_DIR / "Scripts" / "pip.exe"
BIN_DIR      = PROJECT_ROOT / "bin" / "ffmpeg"
FFMPEG_EXE   = BIN_DIR / "ffmpeg.exe"
FFPROBE_EXE  = BIN_DIR / "ffprobe.exe"
CACHE_ROOT   = PROJECT_ROOT / ".cache"
TMP_ROOT     = PROJECT_ROOT / ".tmp"
REQ_FILE     = PROJECT_ROOT / "requirements.txt"
CONFIG_FILE  = PROJECT_ROOT / "config.json"
COOKIES_FILE = PROJECT_ROOT / "cookies.txt"

# PyTorch: nightly cu128 (RTX 5060 / Blackwell sm_120 support)
TORCH_INDEX_URL = "https://download.pytorch.org/whl/nightly/cu128"
TORCH_PACKAGES  = ["torch", "torchvision", "torchaudio"]

# VieNeu extra index (llama_cpp_python prebuilt)
VIENEU_EXTRA_INDEX = "https://pnnbao97.github.io/llama-cpp-python-v0.3.16/cpu/"

# FFmpeg download URLs (thu lan luot)
FFMPEG_URLS = [
    ("https://github.com/BtbN/ffmpeg-builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip", "BtbN static GPL"),
    ("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", "gyan.dev essentials"),
]

# ── Logging helpers ──────────────────────────────────────────────────────────
def ok(msg):   print(f"  {GREEN}✓{RESET}  {msg}")
def info(msg): print(f"  {CYAN}→{RESET}  {msg}")
def warn(msg): print(f"  {YELLOW}!{RESET}  {msg}")
def err(msg):  print(f"  {RED}✗{RESET}  {msg}")
def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*58}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*58}{RESET}")


# ── Helpers ──────────────────────────────────────────────────────────────────
def build_env():
    """Tra ve environ voi cac bien cache tro vao thu muc project."""
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["XDG_CACHE_HOME"]         = str(CACHE_ROOT)
    env["HF_HOME"]                = str(CACHE_ROOT / "huggingface")
    env["HUGGINGFACE_HUB_CACHE"]  = str(CACHE_ROOT / "huggingface" / "hub")
    env["TRANSFORMERS_CACHE"]     = str(CACHE_ROOT / "huggingface" / "transformers")
    env["TORCH_HOME"]             = str(CACHE_ROOT / "torch")
    env["PIP_CACHE_DIR"]          = str(CACHE_ROOT / "pip")
    env["UV_CACHE_DIR"]           = str(CACHE_ROOT / "uv")
    env["TEMP"]                   = str(TMP_ROOT)
    env["TMP"]                    = str(TMP_ROOT)
    env["TMPDIR"]                 = str(TMP_ROOT)
    return env


def run(cmd, **kwargs):
    """subprocess.run voi encoding mac dinh utf-8."""
    return subprocess.run(cmd, encoding="utf-8", errors="replace", **kwargs)


def download_file(url, dest):
    """Tai file voi progress bar. Tra ve True neu thanh cong."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done  = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if total > 0:
                        pct    = min(done / total * 100, 100)
                        filled = int(40 * pct / 100)
                        bar    = "█" * filled + "░" * (40 - filled)
                        print(f"\r  [{bar}] {pct:5.1f}%  {done/1048576:.1f}/{total/1048576:.1f} MB  ",
                              end="", flush=True)
        print()
        return True
    except Exception as e:
        print()
        warn(f"Loi tai: {e}")
        return False


# ── Step 0: Tao cac thu muc va file can thiet ────────────────────────────────
def ensure_project_structure():
    section("BUOC 0/4 — CAU TRUC THU MUC & FILE CAU HINH")

    # Thu muc
    for d in [CACHE_ROOT, TMP_ROOT, PROJECT_ROOT / "output",
              PROJECT_ROOT / "bin" / "ffmpeg", PROJECT_ROOT / "data"]:
        d.mkdir(parents=True, exist_ok=True)
        ok(f"Thu muc: {d.relative_to(PROJECT_ROOT)}")

    # config.json mac dinh
    if not CONFIG_FILE.exists():
        import json
        default_cfg = {
            "source_input": "",
            "cover_mode": "blur",
            "whisper_model": "base",
            "burn_sub": True,
            "subtitle_offset_sec": 0.0,
            "subtitle_timing_scale": 1.0,
            "video_speed": 1.0,
            "subtitle_font_scale": 1.0,
            "subtitle_font_size": 15,
            "subtitle_margin_px": 0,
            "srt_max_chars_per_line": 44,
            "blur_padding_px": 12,
            "cover_offset_px": 0,
            "blur_power": 4,
            "enable_dub": False,
            "dub_mode": "preset",
            "dub_backend_mode": "turbo_gpu",
            "dub_preset_voice": "Bích Ngọc (Nữ - Miền Bắc)",
            "dub_ref_audio": "",
            "dub_ref_text": "",
            "dub_voice_volume": 1.0,
            "dub_source_volume": 0.1,
            "dub_mix_mode": "nen_nho",
            "dub_remote_api_base": "http://localhost:23333/v1",
            "tts_preview_text": "xin chào đây là giọng đọc mẫu"
        }
        CONFIG_FILE.write_text(json.dumps(default_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        ok("Tao config.json mac dinh")
    else:
        info("config.json da ton tai")

    # cookies.txt placeholder
    if not COOKIES_FILE.exists():
        COOKIES_FILE.write_text(
            "# Netscape HTTP Cookie File\n"
            "# Dan cookie Bilibili/YouTube vao day neu can tai video rieng tu.\n"
            "# Dung EditThisCookie (Chrome) de xuat file nay.\n",
            encoding="utf-8"
        )
        ok("Tao cookies.txt (placeholder)")
    else:
        info("cookies.txt da ton tai")

    return True


# ── Step 1: Virtual Environment ──────────────────────────────────────────────
def create_venv():
    section("BUOC 1/4 — VIRTUAL ENVIRONMENT")

    if VENV_PYTHON.exists():
        info("venv da ton tai — kiem tra Python...")
        r = run([str(VENV_PYTHON), "--version"], capture_output=True)
        if r.returncode == 0:
            ok(f"venv Python: {r.stdout.strip()}")
            return True
        warn("venv hong — se tao lai...")
        shutil.rmtree(VENV_DIR, ignore_errors=True)

    info(f"Dang tao virtual environment tai: venv\\")
    r = run([sys.executable, "-m", "venv", str(VENV_DIR)], capture_output=True)
    if r.returncode != 0:
        err(f"Khong the tao venv: {r.stderr.strip()[:200]}")
        return False

    ok("Virtual environment da tao xong")

    # Nang cap pip trong venv
    info("Nang cap pip...")
    run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "-q"],
        capture_output=True, env=build_env())
    ok("pip da duoc nang cap")
    return True


# ── Step 2: FFmpeg ───────────────────────────────────────────────────────────
def install_ffmpeg():
    section("BUOC 2/4 — FFMPEG (STATIC BUILD)")

    if FFMPEG_EXE.exists():
        info("ffmpeg.exe da ton tai — verify...")
        r = run([str(FFMPEG_EXE), "-version"], capture_output=True, timeout=10)
        if r.returncode == 0:
            first = r.stdout.splitlines()[0] if r.stdout else "?"
            ok(f"FFmpeg OK: {first}")
            return True
        warn("ffmpeg hong — se tai lai...")
        for f in BIN_DIR.glob("*.exe"):
            f.unlink(missing_ok=True)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = PROJECT_ROOT / "bin" / "_ffmpeg_dl.zip"

    for url, label in FFMPEG_URLS:
        info(f"Dang tai FFmpeg ({label})...")
        info(f"URL: {url[:72]}...")
        if not download_file(url, zip_path):
            continue

        info("Dang giai nen...")
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                names   = z.namelist()
                targets = [n for n in names if Path(n).name in ("ffmpeg.exe", "ffprobe.exe") and "/bin/" in n]
                if not targets:
                    targets = [n for n in names if Path(n).name in ("ffmpeg.exe", "ffprobe.exe")]
                if not targets:
                    err("Khong tim thay ffmpeg.exe trong zip!")
                    zip_path.unlink(missing_ok=True)
                    continue
                for name in targets:
                    data   = z.read(name)
                    target = BIN_DIR / Path(name).name
                    target.write_bytes(data)
                    ok(f"  Giai nen: {target.name}  ({len(data)/1048576:.1f} MB)")
        except Exception as e:
            err(f"Loi giai nen: {e}")
            zip_path.unlink(missing_ok=True)
            continue

        zip_path.unlink(missing_ok=True)
        r = run([str(FFMPEG_EXE), "-version"], capture_output=True, timeout=10)
        if r.returncode == 0:
            ok("FFmpeg da san sang!")
            return True
        err("Giai nen OK nhung ffmpeg van khong chay — thu URL khac...")
        for f in BIN_DIR.glob("*.exe"):
            f.unlink(missing_ok=True)

    err("Khong the tai FFmpeg tu dong!")
    warn("Hay tai thu cong: https://www.gyan.dev/ffmpeg/builds/ va giai nen vao bin\\ffmpeg\\")
    return False


# ── Step 3: Python packages ──────────────────────────────────────────────────
def install_packages():
    section("BUOC 3/4 — PYTHON PACKAGES")
    env = build_env()

    # Nang cap pip mot lan nua (phong truong hop venv vua tao)
    run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip", "-q"],
        capture_output=True, env=env)

    all_ok = True

    # --- 3a: Core packages tu requirements.txt ---
    if REQ_FILE.exists():
        info(f"Cai packages tu requirements.txt...")
        r = run(
            [str(VENV_PYTHON), "-m", "pip", "install",
             "-r", str(REQ_FILE),
             "--extra-index-url", VIENEU_EXTRA_INDEX,
             "-q", "--no-warn-script-location"],
            env=env,
            text=True
        )
        if r.returncode == 0:
            ok("Tat ca packages trong requirements.txt da cai xong")
        else:
            warn("Mot so package trong requirements.txt that bai, thu cai tung cai...")
            all_ok = _install_fallback(env)
    else:
        warn("Khong tim thay requirements.txt — cai tung package mot...")
        all_ok = _install_fallback(env)

    return all_ok


def _install_fallback(env):
    """Cai tung package mot khi requirements.txt khong hoat dong."""
    CORE_PKGS = [
        "yt-dlp",
        "openai-whisper",
        "deep-translator",
        "librosa",
        "soundfile",
        "pydub",
        "opencv-python-headless",
        "pillow",
        "transformers",
        "accelerate",
        "huggingface_hub",
        "safetensors",
        "tokenizers",
    ]
    all_ok = True
    for pkg in CORE_PKGS:
        info(f"Cai: {pkg}")
        cmd = [str(VENV_PYTHON), "-m", "pip", "install", pkg, "-q", "--no-warn-script-location"]
        r = run(cmd, capture_output=True, env=env)
        if r.returncode == 0:
            ok(f"{pkg} OK")
        else:
            warn(f"{pkg}: {(r.stderr or '').strip()[:100]}")
            all_ok = False

    # vieneu rieng (can extra-index-url)
    info("Cai: vieneu")
    cmd = [str(VENV_PYTHON), "-m", "pip", "install", "vieneu",
           "--extra-index-url", VIENEU_EXTRA_INDEX, "-q", "--no-warn-script-location"]
    r = run(cmd, capture_output=True, env=env)
    if r.returncode == 0:
        ok("vieneu OK")
    else:
        warn(f"vieneu: {(r.stderr or '').strip()[:100]}")
        all_ok = False

    return all_ok


# ── Step 4: PyTorch CUDA ─────────────────────────────────────────────────────
def install_pytorch():
    section("BUOC 4/4 — PYTORCH CUDA (RTX / NVENC / Whisper GPU)")
    env = build_env()

    # Kiem tra hien tai
    info("Kiem tra PyTorch hien tai trong venv...")
    r = run(
        [str(VENV_PYTHON), "-c",
         "import torch; v=torch.__version__; c=torch.cuda.is_available(); "
         "g=torch.cuda.get_device_name(0) if c else 'N/A'; "
         "print(v, c, g)"],
        capture_output=True, timeout=20, env=env
    )
    if r.returncode == 0:
        parts = r.stdout.strip().split(" ", 2)
        version  = parts[0] if len(parts) > 0 else "?"
        cuda_ok  = parts[1] if len(parts) > 1 else "False"
        gpu_name = parts[2] if len(parts) > 2 else "N/A"

        if "True" in cuda_ok:
            ok(f"PyTorch {version} voi CUDA — GPU: {gpu_name}")
            ok("PyTorch da san sang, bo qua cai lai")
            return True
        else:
            warn(f"PyTorch {version} KHONG co CUDA — se cai lai voi cu128...")
    else:
        info("Chua co PyTorch hoac bi loi — se cai moi...")

    # Go phien ban cu
    info("Go PyTorch cu (neu co)...")
    run([str(VENV_PYTHON), "-m", "pip", "uninstall", "-y", "-q",
         "torch", "torchvision", "torchaudio"],
        capture_output=True, env=env)

    # Cai PyTorch Nightly cu128 (RTX 5060 / Blackwell sm_120)
    info(f"Cai PyTorch Nightly CUDA 12.8 (~2.5 GB)...")
    info(f"Index: {TORCH_INDEX_URL}")
    warn("Qua trinh nay co the mat 5-15 phut tuy toc do mang...")
    print()

    r = run(
        [str(VENV_PYTHON), "-m", "pip", "install", "--pre",
         *TORCH_PACKAGES,
         "--index-url", TORCH_INDEX_URL],
        env=env
    )

    if r.returncode != 0:
        err("Cai PyTorch CUDA that bai!")
        warn("Se thu cai stable cu121 thay the...")
        r2 = run(
            [str(VENV_PYTHON), "-m", "pip", "install",
             *TORCH_PACKAGES,
             "--index-url", "https://download.pytorch.org/whl/cu121"],
            env=env
        )
        if r2.returncode != 0:
            err("Cai PyTorch cu121 cung that bai — se chay tren CPU!")
            return False
        warn("Da cai PyTorch cu121 (CPU-only cho RTX 5060, CUDA co the khong hoat dong)")
        return True

    # Verify
    r = run(
        [str(VENV_PYTHON), "-c",
         "import torch; "
         "print(f'PyTorch {torch.__version__}'); "
         "print(f'CUDA: {torch.cuda.is_available()}'); "
         "print(f'GPU: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'GPU: N/A')"],
        capture_output=True, timeout=20, env=env
    )
    if r.returncode == 0:
        for line in r.stdout.strip().splitlines():
            ok(line)
    return True


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{BOLD}{CYAN}{'='*58}{RESET}")
    print(f"{BOLD}{CYAN}  DUBBING EXTRACTOR — TU DONG CAI DAT MOI TRUONG{RESET}")
    print(f"{BOLD}{CYAN}  Python: {sys.version.split()[0]}  |  Platform: Windows{RESET}")
    print(f"{BOLD}{CYAN}  Project: {PROJECT_ROOT}{RESET}")
    print(f"{BOLD}{CYAN}{'='*58}{RESET}\n")

    results = {}

    results["structure"] = ensure_project_structure()
    results["venv"]      = create_venv()
    if not results["venv"]:
        err("Khong the tao venv — dung lai.")
        return 1

    results["ffmpeg"]   = install_ffmpeg()
    results["packages"] = install_packages()
    results["pytorch"]  = install_pytorch()

    # ── Tong ket ────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{CYAN}{'='*58}{RESET}")
    print(f"{BOLD}  KET QUA CAI DAT{RESET}")
    print(f"{BOLD}{CYAN}{'='*58}{RESET}")
    labels = {
        "structure": "Thu muc & file cau hinh",
        "venv":      "Virtual environment",
        "ffmpeg":    "FFmpeg static",
        "packages":  "Python packages",
        "pytorch":   "PyTorch CUDA",
    }
    all_ok = True
    for key, label in labels.items():
        status = results.get(key, False)
        if status:
            print(f"  {GREEN}✓{RESET}  {label}")
        else:
            print(f"  {RED}✗{RESET}  {label}")
            all_ok = False

    print(f"\n{BOLD}{CYAN}{'='*58}{RESET}")
    if all_ok:
        print(f"  {GREEN}{BOLD}CAI DAT HOAN TAT!{RESET}")
        print(f"\n  Buoc tiep theo:")
        print(f"    1. (Neu can) Dan cookie Bilibili vao:  cookies.txt")
        print(f"    2. Chay ung dung:                      run.bat")
    else:
        print(f"  {YELLOW}{BOLD}HOAN TAT VOI MOT SO LOI — xem log ben tren.{RESET}")
        print(f"\n  App van co the chay duoc voi chuc nang han che.")
        print(f"  Chay lai install.bat neu can su dung day du tinh nang.")
    print(f"{BOLD}{CYAN}{'='*58}{RESET}\n")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
