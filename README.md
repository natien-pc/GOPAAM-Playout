# GOPAAM TV Playout & CG — Starter (Python)
This repository is a starter toolkit for a TV playout + CG application in Python. It targets older Windows platforms (XP/Vista/7) where possible — use Python 3.7/3.8 and compatible Qt/OpenCV builds.

* Features

Video playback (file or stream via OpenCV/FFmpeg)
Layered CG engine (15+ layers supported)
Channel logo, sponsor logos, watermark, animated/static images
Clock, back-in timer, program/next/coming-up titles
Cyclic crawl text (news ticker)
RSS feed reader
SMS moderation queue (UI skeleton; integrate with SMS provider)
Simple chroma key utility for live-show compositing
Hooks for gopstream/RTMP/HLS via external FFmpeg integration
* Requirements

Python 3.7 or 3.8 (recommended for older Windows)
pip install -r requirements.txt
FFmpeg installed and on PATH for advanced streaming/encoding tasks
Notes about old Windows compatibility

Pre-built wheels for newer opencv-python and PyQt5 may not run on XP; if targeting XP, find/compile compatible wheels or use older versions of those packages.
Always test on the target Windows version and adjust dependency versions accordingly.
Quickstart

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
Where to extend

Replace sms_moderation.py placeholders with an SMS provider integration (Twilio, Nexmo, etc).
Integrate FFmpeg subprocesses or python-ffmpeg bindings for HLS/RTMP ingest and output.
Replace social_stream placeholder with real social API calls (Twitter/X, Facebook, Instagram), or a local socket feed for moderated content.
License

Starter template — adapt as needed.
