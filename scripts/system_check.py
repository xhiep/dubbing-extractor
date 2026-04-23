import subprocess
import sys
from pathlib import Path

print("="*70)
print("FINAL SYSTEM CHECK")
print("="*70)

VENV_PYTHON = Path("venv/Scripts/python.exe")
FFMPEG = Path("bin/ffmpeg/ffmpeg.exe")

all_ok = True
CACHE_ROOT = Path(".cache")

# 1. Check venv
print("\n[1/6] Checking virtual environment...")
if VENV_PYTHON.exists():
    print("  [OK] venv Python found")
else:
    print("  [FAIL] venv not found")
    all_ok = False

# 2. Check FFmpeg
print("\n[2/6] Checking FFmpeg...")
if FFMPEG.exists():
    result = subprocess.run([str(FFMPEG), "-version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("  [OK] FFmpeg working")
    else:
        print("  [FAIL] FFmpeg not working")
        all_ok = False
else:
    print("  [FAIL] FFmpeg not found")
    all_ok = False

# 3. Check NVENC
print("\n[3/6] Checking NVENC support...")
result = subprocess.run([str(FFMPEG), "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=5)
if "h264_nvenc" in result.stdout:
    print("  [OK] NVENC available")
else:
    print("  [FAIL] NVENC not available")
    all_ok = False

# 4. Check PyTorch
print("\n[4/6] Checking PyTorch...")
result = subprocess.run([str(VENV_PYTHON), "-c", "import torch; print(torch.__version__); print(torch.cuda.is_available())"], capture_output=True, text=True, timeout=10)
if result.returncode == 0:
    lines = result.stdout.strip().split()
    version = lines[0] if lines else "unknown"
    cuda = lines[1] if len(lines) > 1 else "False"
    print(f"  [OK] PyTorch {version}")
    print(f"  [OK] CUDA available: {cuda}")
else:
    print("  [FAIL] PyTorch not working")
    all_ok = False

# 5. Check Whisper
print("\n[5/6] Checking Whisper...")
result = subprocess.run([str(VENV_PYTHON), "-c", "import whisper; print(whisper.__version__)"], capture_output=True, text=True, timeout=10)
if result.returncode == 0:
    version = result.stdout.strip()
    print(f"  [OK] Whisper {version}")
else:
    print("  [FAIL] Whisper not working")
    all_ok = False

print("\n[6/6] Checking VieNeu-TTS + local cache...")
if CACHE_ROOT.exists():
    print("  [OK] Project-local .cache exists")
else:
    print("  [WARN] .cache not found yet (will be created on first run)")
result = subprocess.run(
    [str(VENV_PYTHON), "-c", "import vieneu; print(vieneu.__version__ if hasattr(vieneu, '__version__') else 'installed')"],
    capture_output=True,
    text=True,
    timeout=20,
)
if result.returncode == 0:
    version = result.stdout.strip() or "installed"
    print(f"  [OK] VieNeu-TTS {version}")
else:
    print("  [FAIL] VieNeu-TTS not working")
    all_ok = False

print("\n" + "="*70)
if all_ok:
    print("ALL CHECKS PASSED - SYSTEM READY!")
    print("\nYou can now run: run.bat")
else:
    print("SOME CHECKS FAILED - Please run: install.bat")
print("="*70)

sys.exit(0 if all_ok else 1)
