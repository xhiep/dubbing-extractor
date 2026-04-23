import sys
import os
import ctypes

# Try adding torch library path to dll search directory
import torch
torch_lib_path = os.path.join(os.path.dirname(torch.__file__), 'lib')
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(torch_lib_path)

from src.utils.suppress_warnings import install_stderr_filter
install_stderr_filter()

from src.modules.tts.vieneu_engine import _get_engine

engine = _get_engine(engine_mode="turbo_gpu")
print("Engine loaded")
