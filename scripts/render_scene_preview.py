import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.pexels import fetch_stock_footage_for_scenes
from src.agents.video import generate_elevenlabs_voiceover

def main():
    print("=== Rendering Scene 2 (Terminal Data Card) Preview Clip with Audio ===")

    # 1. Fetch Pexels stock video for Scene 2 (Stock Chart / Trading Desk)
    stock_queries = {
        "scene2": "stock trading chart"
    }
    stock_clips = fetch_stock_footage_for_scenes(stock_queries)

    if not stock_clips.get("scene2"):
        print("[Error] Failed to fetch Pexels stock video for Scene 2. Is PEXELS_API_KEY valid in .env?")
        sys.exit(1)

    print(f"Stock clip downloaded to: remotion/public/{stock_clips['scene2']}")

    # 2. Generate Audio with new Voice ID
    audio_path = Path("remotion/public/audio_parts/preview_test.mp3")
    test_text = "Quantitative setup detected on SNOW. Institutional liquidity suggests a strong long position with a target of 144 dollars."
    print("Generating ElevenLabs TTS for test segment...")
    generate_elevenlabs_voiceover(test_text, audio_path, voice_id="EXAVITQu4vr4xnSDxMaL")

    # 3. Prepare props for Scene 2 exclusively
    props = {
        "ticker": "SNOW",
        "direction": "LONG",
        "price": "$140.32",
        "target": "$144.80",
        "stop": "$137.20",
        "confidence": "46%",
        "headlineText": "Here's a real call we made on SNOW",
        "voiceoverAudioUrl": "audio_parts/preview_test.mp3",
        "primaryColor": "#030712",
        "secondaryColor": "#3B82F6",
        "accentColor": "#10B981",
        "textColor": "#F9FAFB",
        "brandName": "CrowdWisdomTrading",
        "designVariant": "option3_terminal",
        "durationInFrames": 1500,
        "scenes": [
            {"name": "historical_lead", "startFrame": 0, "endFrame": 73},
            {"name": "stat_reveal", "startFrame": 74, "endFrame": 370},
            {"name": "confidence_score", "startFrame": 371, "endFrame": 708},
            {"name": "trader_consensus", "startFrame": 709, "endFrame": 1002},
            {"name": "cta", "startFrame": 1003, "endFrame": 1217}
        ],
        "stockClips": stock_clips
    }

    remotion_dir = Path("remotion")
    props_json_path = remotion_dir / "public" / "preview_props.json"
    output_mp4 = Path("remotion/out/scene2_preview.mp4")

    with open(props_json_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2)

    print(f"Rendering Remotion composition (Frames 74-370) to {output_mp4}...")

    # Render only frames 74 to 370
    cmd = [
        "npx", "remotion", "render",
        "src/index.ts", "AdComposition",
        str(output_mp4.resolve()),
        f"--props={props_json_path.resolve()}",
        "--frames=74-370"
    ]

    res = subprocess.run(
        cmd,
        cwd=remotion_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if res.returncode != 0:
        print("[Remotion Error]")
        print(res.stderr)
        sys.exit(1)

    print(f"Success! Scene 2 preview clip rendered at: {output_mp4.resolve()}")


if __name__ == "__main__":
    main()
