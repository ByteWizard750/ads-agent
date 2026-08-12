import os
import sys
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def generate_synced_audio_and_log():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("[ERROR] ELEVENLABS_API_KEY missing.")
        return

    voice_id = "pNInz6obpgDQGcFmaJgB"
    model_id = "eleven_multilingual_v2"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    sentences = [
        ("scene1_lead", "Here’s a real call we made:"),
        ("scene2_stat", "Our proprietary sentiment signal on SNOW indicated a LONG position when it was at $140.32, targeting $144.80."),
        ("scene3_conf", "Even with a modest 46% confidence level due to limited primary data, our analysis identified strong bullish social sentiment and a supportive technical structure."),
        ("scene4_trader", "This insight came from synthesizing thousands of professional traders' views across platforms, revealing where liquidity and momentum could build."),
        ("scene5_cta", "This is how CrowdWisdomTrading helps you spot opportunities. Claim your free 7-day trial of CrowdWisdomTrading signals now.")
    ]

    temp_dir = Path("remotion/public/audio_parts")
    temp_dir.mkdir(parents=True, exist_ok=True)

    pause_sec = 0.5
    scene_timings = []
    current_time_sec = 0.0
    audio_files = []

    # Generate 0.5s silence file
    silence_file = temp_dir / "silence.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(pause_sec),
        "-q:a", "9", "-acodec", "libmp3lame", str(silence_file)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    print("\n================ REAL AUDIO-VISUAL TIMING MAPPING LOG ================")
    for idx, (scene_name, text) in enumerate(sentences, 1):
        part_file = temp_dir / f"{scene_name}.mp3"
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"ElevenLabs TTS failed: {res.text}")
        
        with open(part_file, "wb") as f:
            f.write(res.content)

        # Get exact duration of this sentence audio clip
        ffprobe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(part_file)
        ]
        duration_sec = float(subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip())
        
        start_frame = int(current_time_sec * 30)
        end_time_sec = current_time_sec + duration_sec
        end_frame = int(end_time_sec * 30)

        scene_timings.append({
            "scene": scene_name,
            "text": text,
            "audio_start_sec": round(current_time_sec, 3),
            "audio_end_sec": round(end_time_sec, 3),
            "visual_start_frame": start_frame,
            "visual_end_frame": end_frame,
            "duration_sec": round(duration_sec, 3)
        })

        audio_files.append(part_file)
        audio_files.append(silence_file)

        current_time_sec = end_time_sec + pause_sec

    # Concatenate all parts into remotion/public/voiceover.mp3
    concat_list_file = temp_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for fpath in audio_files:
            f.write(f"file '{fpath.resolve()}'\n")

    final_audio_path = Path("remotion/public/voiceover.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
        "-c", "copy", str(final_audio_path)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    total_duration_sec = current_time_sec - pause_sec
    total_frames = int(total_duration_sec * 30)

    print(f"Total Combined Audio Duration : {total_duration_sec:.3f} seconds ({total_frames} frames @ 30fps)")
    print("----------------------------------------------------------------------")
    for t in scene_timings:
        print(f"Scene: {t['scene']:15s} | Audio: {t['audio_start_sec']:6.3f}s -> {t['audio_end_sec']:6.3f}s | Visual Frames: {t['visual_start_frame']:4d} -> {t['visual_end_frame']:4d} | Duration: {t['duration_sec']:5.3f}s")
    print("======================================================================\n")

    return scene_timings, total_frames

if __name__ == "__main__":
    generate_synced_audio_and_log()
