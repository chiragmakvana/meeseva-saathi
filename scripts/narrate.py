"""Generate narration clips with Azure AI Speech (neural voices) from a segments JSON file.

Usage: python -m scripts.narrate <segments.json> <out_dir>
segments.json: [{"id": "intro", "voice": "en-IN-NeerjaNeural", "text": "..."}, ...]
Writes <out_dir>/<id>.mp3 and <out_dir>/durations.json ({id: seconds}).
Needs AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env (never committed).
"""
import json
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import httpx
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
KEY, REGION = os.environ["AZURE_SPEECH_KEY"], os.environ.get("AZURE_SPEECH_REGION", "centralindia")
URL = f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
HEADERS = {"Ocp-Apim-Subscription-Key": KEY, "Content-Type": "application/ssml+xml",
           "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3", "User-Agent": "meeseva-saathi-demo"}


def synth(text: str, voice: str, rate: str = "-4%") -> bytes:
    lang = voice[:5]
    ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{lang}">'
            f'<voice name="{voice}"><prosody rate="{rate}">{escape(text)}</prosody></voice></speak>')
    r = httpx.post(URL, content=ssml.encode("utf-8"), headers=HEADERS, timeout=120)
    r.raise_for_status()
    return r.content


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 2)


def main(segments_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    segments = json.loads(Path(segments_path).read_text(encoding="utf-8"))
    durations = {}
    for seg in segments:
        mp3 = out / f"{seg['id']}.mp3"
        mp3.write_bytes(synth(seg["text"], seg.get("voice", "en-IN-NeerjaNeural"), seg.get("rate", "-4%")))
        durations[seg["id"]] = duration(mp3)
        print(f"{seg['id']:<14} {durations[seg['id']]:6.1f}s  {seg.get('voice', '')}")
    (out / "durations.json").write_text(json.dumps(durations, indent=1), encoding="utf-8")
    print(f"total {sum(durations.values()):.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
