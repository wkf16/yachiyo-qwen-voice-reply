#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_REGION = "cn"  # cn | intl
DEFAULT_TARGET_MODEL = "qwen3-tts-vc-2026-01-22"
ENROLLMENT_MODEL = "qwen-voice-enrollment"


def api_base(region: str) -> str:
    return "https://dashscope.aliyuncs.com" if region == "cn" else "https://dashscope-intl.aliyuncs.com"


def infer_mime(path: Path) -> str:
    mt, _ = mimetypes.guess_type(str(path))
    return mt or "audio/mpeg"


def to_data_uri(path: Path, mime: Optional[str] = None) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime or infer_mime(path)};base64,{b64}"


def post_customization(api_key: str, region: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{api_base(region)}/api/v1/services/audio/tts/customization"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=120) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text)
    except HTTPError as e:
        text = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        raise RuntimeError(f"HTTP {e.code}: {text}")
    except URLError as e:
        raise RuntimeError(f"Request failed: {e}")


def cmd_create(args: argparse.Namespace) -> None:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DASHSCOPE_API_KEY")

    audio = Path(args.audio)
    if not audio.exists():
        raise FileNotFoundError(f"Audio file not found: {audio}")

    payload = {
        "model": ENROLLMENT_MODEL,
        "input": {
            "action": "create",
            "target_model": args.target_model,
            "preferred_name": args.name,
            "audio": {
                "data": to_data_uri(audio, args.mime),
            },
        },
    }
    data = post_customization(api_key, args.region, payload)

    voice = data.get("output", {}).get("voice")
    if args.voice_out and voice:
        Path(args.voice_out).write_text(voice + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"voice={voice}")


def cmd_list(args: argparse.Namespace) -> None:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DASHSCOPE_API_KEY")

    payload = {
        "model": ENROLLMENT_MODEL,
        "input": {
            "action": "list",
            **({"target_model": args.target_model} if args.target_model else {}),
        },
    }
    data = post_customization(api_key, args.region, payload)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    voices = data.get("output", {}).get("voices") or []
    if not voices:
        print("No voices found.")
        return

    for v in voices:
        vid = v.get("voice") or v.get("id") or "<unknown>"
        name = v.get("preferred_name") or v.get("name") or ""
        model = v.get("target_model") or ""
        print(f"{vid}\t{name}\t{model}")


def cmd_delete(args: argparse.Namespace) -> None:
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DASHSCOPE_API_KEY")

    payload = {
        "model": ENROLLMENT_MODEL,
        "input": {
            "action": "delete",
            "voice": args.voice,
        },
    }
    data = post_customization(api_key, args.region, payload)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"deleted={args.voice}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Qwen3 TTS voice clone helper")
    p.add_argument("--region", choices=["cn", "intl"], default=DEFAULT_REGION, help="API region")

    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create cloned voice")
    c.add_argument("--audio", required=True, help="Path to audio file (wav/mp3/m4a)")
    c.add_argument("--name", default="custom-voice", help="preferred_name for cloned voice")
    c.add_argument("--target-model", default=DEFAULT_TARGET_MODEL, help="qwen3 tts model that will drive this voice")
    c.add_argument("--mime", default=None, help="Override audio MIME type")
    c.add_argument("--voice-out", default=None, help="Write returned voice id to file")
    c.add_argument("--json", action="store_true", help="Print full JSON response")
    c.set_defaults(func=cmd_create)

    l = sub.add_parser("list", help="List cloned voices")
    l.add_argument("--target-model", default=None, help="Optional filter by target model")
    l.add_argument("--json", action="store_true", help="Print full JSON response")
    l.set_defaults(func=cmd_list)

    d = sub.add_parser("delete", help="Delete cloned voice")
    d.add_argument("--voice", required=True, help="Voice ID")
    d.add_argument("--json", action="store_true", help="Print full JSON response")
    d.set_defaults(func=cmd_delete)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
