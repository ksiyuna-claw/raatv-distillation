#!/usr/bin/env python3
"""
Concurrent Audio Download + ASR Transcription — Phase 1
Uses ThreadPoolExecutor(10) to maximize TikHub QPS (10/s)

Features:
  - 10x parallel download + ASR
  - Checkpoint resume (re-run skips completed items)
  - Smart audio URL priority (audio_fallback > audio > video)
  - Auto-compress long audio (>25MB) with ffmpeg
  - Music URLs always skipped (no speech content)

Usage:
  python3 download_asr_concurrent.py \
    --selected metadata/selected_50.json \
    --audio-dir audio/ \
    --status status/status.json \
    --transcripts transcripts.json \
    --tikhub-key "YOUR_TIKHUB_API_KEY" \
    --sf-key "YOUR_SILICONFLOW_KEY"

Optional:
  --proxy "http://your-proxy:port"  Proxy for API calls (defaults to none)
"""

import argparse, json, os, sys, time, subprocess, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

TIKHUB_BASE = "https://api.tikhub.dev"
SILICONFLOW_BASE = "https://api.siliconflow.cn/v1/audio/transcriptions"
MAX_WORKERS = 10


def get_video_detail(aweme_id, api_key, proxy=None):
    """Fetch video details (including audio URLs) via TikHub"""
    url = f"{TIKHUB_BASE}/api/v1/douyin/web/fetch_one_video?aweme_id={aweme_id}"
    headers = {"Authorization": f"Bearer {api_key}", "User-Agent": "curl/7.88.1"}
    req = urllib.request.Request(url, headers=headers)
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({"https": proxy, "http": proxy})
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()
    for attempt in range(3):
        try:
            with opener.open(req, timeout=60) as resp:
                data = json.loads(resp.read())
            item = data.get("data", {}).get("aweme_detail", {}) or data.get("data", {})
            music = item.get("music", {})
            video = item.get("video", {})
            url_prio = [
                ("audio_fallback", music.get("audio_fallback_url")),
                ("audio_url", music.get("play_url", {}).get("uri")),
                ("video_url", video.get("play_addr", {}).get("url_list", [None])[0]),
            ]
            return {
                "aweme_id": aweme_id,
                "desc": item.get("desc", ""),
                "duration": item.get("duration", 0),
                "audio_urls": [(label, u) for label, u in url_prio if u],
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
    return {"aweme_id": aweme_id, "error": "tikhub_failed"}


def download_audio(aweme_id, urls, audio_dir, proxy=None):
    """Download audio file, trying multiple URLs by priority"""
    os.makedirs(audio_dir, exist_ok=True)
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({"https": proxy, "http": proxy})
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()
    for label, url in urls:
        if "music" in label.lower():
            continue  # Never use music URLs — pure BGM, no speech
        path = os.path.join(audio_dir, f"{aweme_id}.mp3")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.88.1"})
            with opener.open(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1024:
                continue
            with open(path, "wb") as f:
                f.write(data)
            return path
        except:
            continue
    return None


def run_asr(audio_path, api_key, proxy=None):
    """
    SiliconFlow ASR via curl subprocess.
    
    NOTE: Must use curl, not python urllib — urllib's multipart encoding
    is incompatible with SiliconFlow's server for large files (returns 500).
    """
    # Compress if >25MB
    if os.path.getsize(audio_path) > 25 * 1024 * 1024:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        subprocess.run(["ffmpeg", "-y", "-i", audio_path, "-acodec", "libmp3lame",
            "-b:a", "32k", tmp], capture_output=True, timeout=60)
        audio_path = tmp

    # Build curl command
    cmd = [
        "curl", "-s", "-X", "POST", SILICONFLOW_BASE,
        "-H", f"Authorization: Bearer {api_key}",
        "-F", "model=FunAudioLLM/SenseVoiceSmall",
        "-F", f"file=@{audio_path}",
    ]
    
    env = os.environ.copy()
    if proxy:
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy

    for attempt in range(2):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
            resp = json.loads(result.stdout)
            text = resp.get("text", "")
            if text and len(text) >= 10:
                return text
        except:
            pass
        if attempt < 1:
            time.sleep(1)
    return ""


def process_one(video, api_key, audio_dir, sf_key, proxy):
    """Process a single video: fetch detail → download audio → ASR"""
    aweme_id = video.get("aweme_id", "")
    try:
        # Step 1: Get video details
        detail = get_video_detail(aweme_id, api_key, proxy)
        if "error" in detail:
            return {"aweme_id": aweme_id, "status": "error", "error": detail["error"]}

        # Step 2: Download audio
        audio_path = download_audio(aweme_id, detail.get("audio_urls", []), audio_dir, proxy)
        if not audio_path:
            return {"aweme_id": aweme_id, "status": "error", "error": "no_audio"}

        # Step 3: ASR
        text = run_asr(audio_path, sf_key, proxy)
        if not text or len(text) < 10:
            return {"aweme_id": aweme_id, "status": "error", "error": "asr_empty"}

        return {"aweme_id": aweme_id, "status": "done", "text": text, "desc": detail.get("desc", ""),
                "duration": detail.get("duration", 0)}
    except Exception as e:
        return {"aweme_id": aweme_id, "status": "error", "error": str(e)[:100]}


def main():
    p = argparse.ArgumentParser(description="Concurrent audio download + ASR transcription")
    p.add_argument("--selected", required=True, help="Path to selected_50.json")
    p.add_argument("--audio-dir", default="audio/", help="Audio download directory")
    p.add_argument("--status", default="status.json", help="Checkpoint status file")
    p.add_argument("--transcripts", default="transcripts.json", help="Output transcripts file")
    p.add_argument("--tikhub-key", default=os.environ.get("TIKHUB_API_KEY", ""), help="TikHub API Key")
    p.add_argument("--sf-key", default=os.environ.get("SILICONFLOW_KEY", ""), help="SiliconFlow API Key")
    p.add_argument("--proxy", default="", help="Proxy address (e.g., http://your-proxy:port)")
    args = p.parse_args()

    if not args.tikhub_key:
        print("❌ TikHub API Key required (--tikhub-key or env var TIKHUB_API_KEY)")
        sys.exit(1)
    if not args.sf_key:
        print("❌ SiliconFlow API Key required (--sf-key or env var SILICONFLOW_KEY)")
        sys.exit(1)

    proxy = args.proxy or None

    # Load selected videos
    with open(args.selected) as f:
        videos = json.load(f)
    print(f"Selected: {len(videos)} videos")

    # Load completed items (checkpoint resume)
    done_ids = set()
    if os.path.exists(args.status):
        with open(args.status) as f:
            for k, v in json.load(f).items():
                if isinstance(v, dict) and v.get("status") == "done":
                    done_ids.add(k)

    pending = [v for v in videos if v.get("aweme_id") not in done_ids]
    print(f"Completed: {len(done_ids)}, Pending: {len(pending)}")

    # Concurrent processing
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_one, v, args.tikhub_key, args.audio_dir, args.sf_key, proxy): v
                   for v in pending}
        for f in as_completed(futures):
            r = f.result()
            results[r["aweme_id"]] = r
            # Write checkpoint after each item
            with open(args.status, "w") as s:
                json.dump(results, s, ensure_ascii=False, indent=2)
            if r["status"] == "done":
                print(f"  ✅ {r['aweme_id']} ({len(r.get('text',''))} chars)")

    # Merge transcripts
    transcripts = {}
    if os.path.exists(args.status):
        with open(args.status) as f:
            for k, v in json.load(f).items():
                if isinstance(v, dict) and v.get("status") == "done":
                    transcripts[k] = {"text": v["text"], "desc": v.get("desc", ""), "duration": v.get("duration", 0)}
    with open(args.transcripts, "w") as f:
        json.dump(transcripts, f, ensure_ascii=False, indent=2)

    done = sum(1 for v in transcripts.values())
    errors = sum(1 for v in results.values() if v.get("status") == "error")
    print(f"\nDone: {done} transcripts, Errors: {errors}")


if __name__ == "__main__":
    main()
