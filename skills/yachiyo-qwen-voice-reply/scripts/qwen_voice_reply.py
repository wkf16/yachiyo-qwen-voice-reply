#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Optional

DEFAULT_API_KEY = "DASHSCOPE_API_KEY_PLACEHOLDER"
DEFAULT_MODEL = "qwen3-tts-vc-2026-01-22"
DEFAULT_VOICE = "qwen-tts-vc-guanyu-voice-20260216143709994-f294"
MIN_AUDIO_BYTES = 1024


def ensure_dashscope():
    try:
        import dashscope  # type: ignore
        return dashscope
    except Exception as e:
        raise RuntimeError(
            "dashscope 未安装。请先执行: source /Users/doosam/.openclaw/workspace/.venv-qwen/bin/activate && pip install dashscope"
        ) from e


def _extract_audio_url(resp) -> Optional[str]:
    output = resp.output if hasattr(resp, "output") else {}
    if isinstance(output, dict):
        return (output.get("audio") or {}).get("url")
    return output.audio.get("url") if getattr(output, "audio", None) else None


def _download_with_validation(url: str, out_file: Path, retries: int = 3) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    last_err: Optional[Exception] = None

    for i in range(retries):
        try:
            urllib.request.urlretrieve(url, str(out_file))
            if not out_file.exists() or out_file.stat().st_size < MIN_AUDIO_BYTES:
                raise RuntimeError(
                    f"下载到的音频文件异常（大小={out_file.stat().st_size if out_file.exists() else 0} bytes）"
                )
            return
        except Exception as e:
            last_err = e
            if i < retries - 1:
                time.sleep(0.8 * (i + 1))

    raise RuntimeError(f"音频下载失败（重试 {retries} 次后仍失败）：{last_err}")


def synthesize_to_audio_file(text: str, model: str, voice: str, api_key: str, out_audio: Path) -> None:
    dashscope = ensure_dashscope()

    resp = dashscope.MultiModalConversation.call(
        model=model,
        api_key=api_key,
        text=text,
        voice=voice,
        stream=False,
    )

    url = _extract_audio_url(resp)
    if not url:
        raise RuntimeError(f"合成失败，未拿到音频 URL: {resp}")

    _download_with_validation(url, out_audio)


def to_telegram_voice(in_audio: Path, out_ogg: Path) -> None:
    out_ogg.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(in_audio),
        "-c:a", "libopus", "-b:a", "32k", "-vbr", "on", "-ac", "1", "-ar", "48000",
        str(out_ogg),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg 转码失败: {proc.stderr.strip()}")

    if not out_ogg.exists() or out_ogg.stat().st_size < MIN_AUDIO_BYTES:
        raise RuntimeError(
            f"转码后音频异常（大小={out_ogg.stat().st_size if out_ogg.exists() else 0} bytes）"
        )


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Qwen voice reply and output MEDIA path")
    p.add_argument("text", help="Text to speak")
    p.add_argument("--voice", default=DEFAULT_VOICE)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--out", default="", help="Optional output ogg path")
    args = p.parse_args()

    api_key = os.getenv("DASHSCOPE_API_KEY") or DEFAULT_API_KEY
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY")

    with tempfile.TemporaryDirectory(prefix="qwen-voice-reply-") as td:
        tmp_audio = Path(td) / "tts_input_audio.bin"
        if args.out:
            out_ogg = Path(args.out)
        else:
            out_ogg = Path(tempfile.gettempdir()) / f"yachiyo-voice-{next(tempfile._get_candidate_names())}.ogg"

        synthesize_to_audio_file(args.text, args.model, args.voice, api_key, tmp_audio)
        to_telegram_voice(tmp_audio, out_ogg)

    print("[[audio_as_voice]]")
    print(f"MEDIA:{out_ogg}")


if __name__ == "__main__":
    main()
