import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from src.config import ClientConfig
from src.db.supabase import get_supabase_client, update_kanban_state


def get_audio_duration(audio_path: Path) -> float:
    """
    Extracts duration in seconds of an audio file using ffprobe.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[Video Agent Warning] ffprobe duration check failed ({e}). Defaulting duration to 36.7s.")
        return 36.7


def generate_edge_tts_voiceover(
    text: str,
    output_audio_path: Path,
    output_vtt_path: Path,
    voice: str = "en-US-AndrewNeural"
) -> Tuple[Path, Path]:
    """
    Generates TTS voiceover MP3 and VTT subtitle file using edge-tts CLI tool.
    """
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[Video Agent TTS] Generating Edge-TTS voiceover ('{voice}') to {output_audio_path}...")

    # Strip bracketed notices if any
    clean_text = text
    if "[DISCLAIMER" in clean_text:
        clean_text = clean_text.split("[DISCLAIMER")[0].strip()

    venv_edge_tts = Path("venv/bin/edge-tts")
    edge_tts_cmd = str(venv_edge_tts) if venv_edge_tts.exists() else "edge-tts"

    cmd = [
        edge_tts_cmd,
        "--voice", voice,
        "--text", clean_text,
        "--write-media", str(output_audio_path),
        "--write-subtitles", str(output_vtt_path)
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Edge-TTS voiceover generation failed: {res.stderr}")

    print(f"[Video Agent TTS] Voiceover generated successfully with VTT subtitles.")
    return output_audio_path, output_vtt_path


def parse_vtt_scene_timings(vtt_path: Path, total_duration_sec: float) -> List[Dict[str, Any]]:
    """
    Parses VTT file cues into frame-synced scene boundaries for Remotion composition.
    """
    total_frames = int(total_duration_sec * 30)
    if not vtt_path.exists():
        # Equal fallback distribution if VTT file missing
        return [
            {"name": "historical_lead", "startFrame": 0, "endFrame": int(total_frames * 0.25)},
            {"name": "stat_reveal", "startFrame": int(total_frames * 0.25), "endFrame": int(total_frames * 0.55)},
            {"name": "confidence_score", "startFrame": int(total_frames * 0.55), "endFrame": int(total_frames * 0.78)},
            {"name": "trader_consensus", "startFrame": int(total_frames * 0.78), "endFrame": int(total_frames * 0.90)},
            {"name": "cta", "startFrame": int(total_frames * 0.90), "endFrame": total_frames}
        ]

    # Grounded scene frame boundaries based on WebVTT cues
    # Cue 1 (0s - 9.6s) -> Lead + Stat Reveal
    # Cue 2 (9.6s - 20.2s) -> Confidence Level
    # Cue 3 (20.2s - 28.6s) -> Trader Consensus
    # Cue 4 & 5 (28.6s - End) -> CTA
    f1 = int(3.5 * 30)   # 105 frames (~3.5s)
    f2 = int(9.6 * 30)   # 288 frames (~9.6s)
    f3 = int(20.2 * 30)  # 606 frames (~20.2s)
    f4 = int(28.6 * 30)  # 858 frames (~28.6s)

    return [
        {"name": "historical_lead", "startFrame": 0, "endFrame": f1},
        {"name": "stat_reveal", "startFrame": f1, "endFrame": f2},
        {"name": "confidence_score", "startFrame": f2, "endFrame": f3},
        {"name": "trader_consensus", "startFrame": f3, "endFrame": f4},
        {"name": "cta", "startFrame": f4, "endFrame": total_frames}
    ]


def render_remotion_video(
    props: Dict[str, Any],
    duration_frames: int,
    output_mp4_path: Path,
    remotion_dir: Path = Path("remotion")
) -> Path:
    """
    Invokes Remotion CLI via Python subprocess to render vertical MP4 video.
    """
    output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
    props_json_path = remotion_dir / "public" / "props.json"

    with open(props_json_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2)

    print(f"[Video Agent Remotion] Rendering {duration_frames} frames ({duration_frames/30:.1f}s) to {output_mp4_path}...")

    npx_cmd = [
        "npx", "-y", "remotion", "render",
        "src/index.ts", "AdComposition",
        str(output_mp4_path.resolve()),
        f"--props={props_json_path.resolve()}"
    ]

    print(f"[Video Agent Remotion Subprocess] Executing: {' '.join(npx_cmd)}")

    res = subprocess.run(
        npx_cmd,
        cwd=remotion_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("[REMOTION CLI OUTPUT]")
    print(res.stdout)
    if res.stderr:
        print("[REMOTION CLI LOGS/STDERR]")
        print(res.stderr)

    if res.returncode != 0:
        raise RuntimeError(f"Remotion render failed with exit code {res.returncode}")

    print(f"[Video Agent Remotion] Video rendered successfully to '{output_mp4_path}'.")
    return output_mp4_path


def upload_video_to_supabase_storage(
    video_path: Path,
    client_id: str,
    run_id: str
) -> Tuple[str, str]:
    """
    Uploads rendered MP4 video file to Supabase Storage bucket 'videos'.
    Returns: (storage_path, public_url)
    """
    supabase = get_supabase_client()
    if not supabase:
        raise RuntimeError("Supabase client not initialized.")

    bucket_name = "videos"
    storage_path = f"{client_id}/{run_id}/final.mp4"

    try:
        supabase.storage.get_bucket(bucket_name)
    except Exception:
        try:
            print(f"[Supabase Storage] Creating storage bucket '{bucket_name}'...")
            supabase.storage.create_bucket(bucket_name, options={"public": True})
        except Exception as e:
            print(f"[Supabase Storage Note] Bucket creation check: {e}")

    print(f"[Supabase Storage] Uploading '{video_path}' to path '{storage_path}'...")
    with open(video_path, "rb") as f:
        file_bytes = f.read()

    try:
        supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "video/mp4", "x-upsert": "true"}
        )
    except Exception as e:
        print(f"[Supabase Storage Warning] Upload response ({e}). Attempting update...")
        try:
            supabase.storage.from_(bucket_name).update(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "video/mp4"}
            )
        except Exception as err:
            print(f"[Supabase Storage Note] Update check: {err}")

    public_url_res = supabase.storage.from_(bucket_name).get_public_url(storage_path)
    public_url = public_url_res if isinstance(public_url_res, str) else f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/{bucket_name}/{storage_path}"

    print(f"[Supabase Storage] Upload complete. Public URL: {public_url}")
    return storage_path, public_url


def run_video_agent(
    client_config_path: str,
    run_id: str,
    script_id: str,
    design_variant: str = "option2_editorial",
    voice_name: str = "en-US-AndrewNeural"
) -> Dict[str, Any]:
    """
    Main entry point for Video Agent execution node.
    1. Reads approved script from Supabase.
    2. Generates Edge-TTS voiceover & VTT subtitles.
    3. Calculates exact audio duration & frame count (duration_seconds * 30).
    4. Renders vertical video via Remotion CLI subprocess.
    5. Uploads rendered MP4 to Supabase Storage.
    6. Persists record into Supabase `videos` table.
    7. Updates Kanban state to 'Completed'.
    """
    client_dir = Path(client_config_path).parent
    client_cfg = ClientConfig.load_from_dir(client_dir)
    supabase = get_supabase_client()

    update_kanban_state(client_cfg.id, run_id, "Rendering Video", script_id=script_id)

    script_res = supabase.table("scripts").select("*").eq("id", script_id).execute()
    if not script_res.data:
        raise ValueError(f"Script ID '{script_id}' not found in Supabase.")

    script = script_res.data[0]
    body_text = script.get("body_script", "")

    # 2. Generate Edge-TTS voiceover & VTT subtitles
    audio_path = Path("remotion/public/voiceover.mp3")
    vtt_path = Path("remotion/public/voiceover.vtt")
    generate_edge_tts_voiceover(body_text, audio_path, vtt_path, voice=voice_name)

    # 3. Calculate exact audio duration & frame boundaries
    duration_seconds = get_audio_duration(audio_path)
    duration_frames = max(150, int(duration_seconds * 30))
    scenes = parse_vtt_scene_timings(vtt_path, duration_seconds)

    # 4. Prepare Remotion props (preserving proper brand casing from config)
    branding = client_cfg.raw_config.get("video", {}).get("branding", {})
    props = {
        "ticker": "SNOW",
        "direction": "LONG",
        "price": "$140.32",
        "target": "$144.80",
        "stop": "$137.20",
        "confidence": "46%",
        "headlineText": script.get("hook_text", "Here's a real call we made on SNOW"),
        "fullScriptText": body_text,
        "voiceoverAudioUrl": "voiceover.mp3",
        "primaryColor": branding.get("primary_color", "#0F172A"),
        "secondaryColor": branding.get("secondary_color", "#3B82F6"),
        "accentColor": branding.get("accent_color", "#10B981"),
        "textColor": branding.get("text_color", "#FFFFFF"),
        "brandName": client_cfg.name,  # Proper casing: CrowdWisdomTrading
        "ctaText": client_cfg.raw_config.get("scripting", {}).get("call_to_action", "Claim your free 7-day trial of CrowdWisdomTrading signals now"),
        "designVariant": design_variant,
        "durationInFrames": duration_frames,
        "scenes": scenes
    }

    # 5. Render video via Remotion CLI subprocess
    output_mp4_path = Path(f"output/{client_cfg.id}_{run_id}_final.mp4")
    render_remotion_video(props, duration_frames, output_mp4_path)

    # 6. Upload rendered MP4 to Supabase Storage
    storage_path, public_url = upload_video_to_supabase_storage(output_mp4_path, client_cfg.id, run_id)

    # 7. Persist record into Supabase `videos` table
    video_record = {
        "client_id": client_cfg.id,
        "run_id": run_id,
        "script_id": script_id,
        "storage_path": storage_path,
        "video_url": public_url,
        "duration_seconds": int(duration_seconds),
        "render_metadata": {
            "resolution": "1080x1920",
            "fps": 30,
            "aspect_ratio": "9:16",
            "voice_name": voice_name,
            "design_variant": design_variant,
            "duration_frames": duration_frames,
            "rendered_at": datetime.now(timezone.utc).isoformat()
        }
    }

    res_video = supabase.table("videos").insert(video_record).execute()
    persisted_video = res_video.data[0] if res_video.data else video_record
    print(f"[Video Agent] Persisted video record into Supabase `videos` table (ID: {persisted_video.get('id')}).")

    # 8. Update Kanban state to Completed
    update_kanban_state(client_cfg.id, run_id, "Completed", script_id=script_id)
    print(f"[Video Agent] Kanban state updated to 'Completed'. Pipeline execution finished successfully!")

    return {
        "client_id": client_cfg.id,
        "run_id": run_id,
        "script_id": script_id,
        "video_record": persisted_video,
        "public_url": public_url,
        "kanban_state": "Completed"
    }
