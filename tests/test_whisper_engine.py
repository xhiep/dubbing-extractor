import unittest
from pathlib import Path
from unittest.mock import patch

from src.modules.transcription import whisper_engine


class _DummyModel:
    def __init__(self, result):
        self.result = result
        self.moved_to_cpu = False

    def cpu(self):
        self.moved_to_cpu = True

    def transcribe(self, *_args, **_kwargs):
        return self.result


class WhisperEngineTests(unittest.TestCase):
    def test_transcribe_releases_model_after_success(self):
        dummy = _DummyModel({"segments": [{"start": 0.0, "end": 1.0, "text": "ok"}], "language": "zh"})

        def fake_load_model(*_args, **_kwargs):
            whisper_engine._active_model = dummy
            return dummy

        with patch.object(whisper_engine, "LOCAL_FFMPEG", Path("C:/ffmpeg/ffmpeg.exe")):
            with patch.object(whisper_engine.torch.cuda, "is_available", return_value=False):
                with patch.object(whisper_engine, "_load_model", side_effect=fake_load_model):
                    segments = whisper_engine.transcribe(Path("audio.mp3"))

        self.assertEqual(len(segments), 1)
        self.assertIsNone(whisper_engine._active_model)
        self.assertTrue(dummy.moved_to_cpu)

    def test_transcribe_falls_back_to_cpu_on_cuda_oom(self):
        calls = []
        models = []

        def fake_load_model(_model_name, device):
            calls.append(device)
            if device == "cuda":
                raise RuntimeError("CUDA out of memory")
            model = _DummyModel({"segments": [{"start": 0.0, "end": 0.5, "text": "cpu"}], "language": "zh"})
            whisper_engine._active_model = model
            models.append(model)
            return model

        with patch.object(whisper_engine, "LOCAL_FFMPEG", Path("C:/ffmpeg/ffmpeg.exe")):
            with patch.object(whisper_engine.torch.cuda, "is_available", return_value=True):
                with patch.object(whisper_engine.torch.cuda, "get_device_name", return_value="Fake GPU"):
                    with patch.object(whisper_engine.torch.cuda, "empty_cache", return_value=None):
                        with patch.object(whisper_engine, "_load_model", side_effect=fake_load_model):
                            segments = whisper_engine.transcribe(Path("audio.mp3"))

        self.assertEqual(calls, ["cuda", "cpu"])
        self.assertEqual(segments[0]["text"], "cpu")
        self.assertIsNone(whisper_engine._active_model)
        self.assertTrue(models[0].moved_to_cpu)


if __name__ == "__main__":
    unittest.main()
