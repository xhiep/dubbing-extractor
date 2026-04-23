"""Translation using deep-translator (batch mode)."""
import time

from deep_translator import GoogleTranslator

from ...config import config

# Gộp tối đa 50 câu/request — an toàn với Google rate limit
_BATCH_SIZE = 50


def translate(segments: list, log_cb=None) -> list:
    def _log(m): log_cb and log_cb(m)

    target_lang = config["target_language"]
    total = len(segments)
    _log(f"->  Dich {total} cau (batch {_BATCH_SIZE})...")

    texts = [seg["text"].strip() for seg in segments]
    translated: list[str] = []
    errors = 0

    batches = [texts[i:i + _BATCH_SIZE] for i in range(0, total, _BATCH_SIZE)]
    done = 0
    for batch in batches:
        tr = GoogleTranslator(source="auto", target=target_lang)
        try:
            results = tr.translate_batch(batch)
            # translate_batch có thể trả None cho câu rỗng
            results = [r or batch[j] for j, r in enumerate(results)]
        except Exception:
            results = list(batch)
            errors += len(batch)
        translated.extend(results)
        done += len(batch)
        if log_cb:
            try:
                log_cb(f"__PROGRESS__{done/total*100:.1f}",
                       f"  Dich [{done}/{total}]")
            except TypeError:
                log_cb(f"  Dich [{done}/{total}]")
        if done < total:
            time.sleep(0.3)  # nghỉ ngắn giữa các batch

    out = []
    for seg, orig, vi in zip(segments, texts, translated):
        out.append({
            "start": seg["start"],
            "end": seg["end"],
            "original": orig,
            "text": vi or orig,
        })

    _log(f"✓  Dich xong ({errors} loi)")
    return out

# ─── CORE: XUẤT FILE ─────────────────────────────────────────────────────────
