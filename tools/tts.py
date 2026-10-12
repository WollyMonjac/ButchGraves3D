"""Neural text-to-speech (Kokoro, 82M, ONNX) for the voice lines, with espeak-ng as the fallback.
Model files (from the kokoro-onnx GitHub releases, model-files-v1.0): kokoro-v1.0.onnx and voices-v1.0.bin in tools/kokoro/
(or $KOKORO_DIR). Set BG_TTS=espeak to use the old espeak-ng/MBROLA voices."""
import os
import numpy as np

_here = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kokoro')
KDIR = os.environ.get('KOKORO_DIR') or (_here if os.path.isdir(_here) else '/home/claude/tts')
_k = None


def available():
    if os.environ.get('BG_TTS', '') == 'espeak':
        return False
    try:
        import kokoro_onnx  # noqa
    except Exception:
        return False
    return os.path.exists(os.path.join(KDIR, 'kokoro-v1.0.onnx'))


def engine():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(KDIR, 'kokoro-v1.0.onnx'), os.path.join(KDIR, 'voices-v1.0.bin'))
    return _k


def style(spec):
    """'am_fenrir' or a blend like 'am_fenrir*0.65+am_onyx*0.35'."""
    k = engine()
    if '+' not in spec and '*' not in spec:
        return spec
    st = 0
    for part in spec.split('+'):
        name, w = (part.split('*') + ['1'])[:2]
        st = st + k.get_voice_style(name.strip()) * float(w)
    return st


def say(text, spec, speed=1.0, path=None):
    """Synthesize text; returns (float samples, sample rate) and optionally writes a 16-bit wav.
    spec may end in '@<lang>' (e.g. 'em_alex@es') for a voice speaking another language."""
    lang = 'en-us'
    if '@' in spec:
        spec, lang = spec.split('@')
    s, sr = engine().create(text, voice=style(spec), speed=speed, lang=lang)
    s = np.asarray(s, np.float32)
    if path:
        import wave
        with wave.open(path, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(s, -1, 1) * 32767).astype(np.int16).tobytes())
    return s, sr


BUTCH = 'am_fenrir*0.65+am_onyx*0.35'     # gravelly, a bit lower than fenrir alone
