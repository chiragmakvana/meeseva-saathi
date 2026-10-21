"""Mix the narration clips into the recorded demo at the timestamps the recorder wrote, and encode to MP4.

Usage: python -m scripts.build_demo_video [docs/demo] [SvaKritAI_Demo.mp4]
Inputs: <dir>/demo_raw.webm, <dir>/timestamps.json, <dir>/audio/<id>.mp3 (from scripts/narrate.py)
"""
import json
import subprocess
import sys
from pathlib import Path


def main(demo_dir: str = "docs/demo", out_name: str = "SvaKritAI_Demo.mp4") -> None:
    d = Path(demo_dir)
    ts = json.loads((d / "timestamps.json").read_text(encoding="utf-8"))
    stamps, total = ts["stamps"], ts["total"]
    ids = [i for i in stamps if (d / "audio" / f"{i}.mp3").exists()]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(d / "demo_raw.webm")]
    for i in ids:
        cmd += ["-i", str(d / "audio" / f"{i}.mp3")]
    delays = "".join(f"[{n + 1}]adelay={int(stamps[i] * 1000)}|{int(stamps[i] * 1000)}[a{n}];" for n, i in enumerate(ids))
    mix = "".join(f"[a{n}]" for n in range(len(ids))) + f"amix=inputs={len(ids)}:normalize=0:dropout_transition=0[aout]"
    cmd += ["-filter_complex", delays + mix, "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-t", f"{total + 1.5:.2f}", "-movflags", "+faststart", str(d / out_name)]
    subprocess.run(cmd, check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(d / out_name)],
                         capture_output=True, text=True).stdout.strip()
    print(f"{d / out_name}: {float(dur):.0f} s")


if __name__ == "__main__":
    main(*sys.argv[1:])
