import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { AdCompositionProps } from "./types";

export const AdComposition: React.FC<AdCompositionProps> = ({
  ticker = "SNOW",
  direction = "LONG",
  price = "$140.32",
  target = "$144.80",
  stop = "$137.20",
  confidence = "46%",
  voiceoverAudioUrl = "voiceover.mp3",
  primaryColor = "#030712",
  secondaryColor = "#3B82F6",
  accentColor = "#10B981",
  textColor = "#F9FAFB",
  brandName = "CrowdWisdomTrading",
  ctaText = "Claim your free 7-day trial of CrowdWisdomTrading signals now",
  scenes,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Real WebVTT audio-synced scene frame boundaries (matching real audio timing log)
  const s1Start = scenes?.[0]?.startFrame ?? 0;
  const s1End = scenes?.[0]?.endFrame ?? 59;

  const s2Start = scenes?.[1]?.startFrame ?? 74;
  const s2End = scenes?.[1]?.endFrame ?? 370;

  const s3Start = scenes?.[2]?.startFrame ?? 385;
  const s3End = scenes?.[2]?.endFrame ?? 708;

  const s4Start = scenes?.[3]?.startFrame ?? 723;
  const s4End = scenes?.[3]?.endFrame ?? 1003;

  const s5Start = scenes?.[4]?.startFrame ?? 1018;
  const s5End = scenes?.[4]?.endFrame ?? (durationInFrames || 1266);

  // Parallax motion design layers: continuous background scale and drift
  const bgScale = 1 + (frame / (durationInFrames || 1200)) * 0.08;
  const bgPanY = (frame / (durationInFrames || 1200)) * -40;
  const midlayerPanY = (frame / (durationInFrames || 1200)) * -15;

  // Spring physics easing curves for tactile motion
  const springCfg = { damping: 18, stiffness: 85, mass: 1.0 };
  const s1Spring = spring({ frame: frame - s1Start, fps, config: springCfg });
  const s2Spring = spring({ frame: frame - s2Start, fps, config: springCfg });
  const s3Spring = spring({ frame: frame - s3Start, fps, config: springCfg });
  const s4Spring = spring({ frame: frame - s4Start, fps, config: springCfg });
  const s5Spring = spring({ frame: frame - s5Start, fps, config: springCfg });

  // Smooth opacity interpolations with 12-frame crossfades
  const fade = 12;
  const o1 = interpolate(frame, [s1Start, s1Start + fade, s1End - fade, s1End], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const o2 = interpolate(frame, [s2Start, s2Start + fade, s2End - fade, s2End], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const o3 = interpolate(frame, [s3Start, s3Start + fade, s3End - fade, s3End], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const o4 = interpolate(frame, [s4Start, s4Start + fade, s4End - fade, s4End], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const o5 = interpolate(frame, [s5Start, s5Start + fade, durationInFrames - 5, durationInFrames], [0, 1, 1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Ticking confidence score (0% -> 46%) synced to Scene 3 audio start
  const rawConfidence = parseInt(confidence.replace("%", ""), 10) || 46;
  const currentConfidence = Math.round(
    interpolate(frame, [s3Start + 10, s3Start + 60], [0, rawConfidence], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: primaryColor,
        fontFamily: "'Inter', monospace, sans-serif",
        color: textColor,
        overflow: "hidden",
      }}
    >
      {/* Background Parallax Layer: Slow Continuous Zoom & Pan Grid */}
      <div
        style={{
          position: "absolute",
          inset: -100,
          backgroundImage: "linear-gradient(#111827 1px, transparent 1px), linear-gradient(90deg, #111827 1px, transparent 1px)",
          backgroundSize: "40px 40px",
          opacity: 0.45,
          transform: `scale(${bgScale}) translateY(${bgPanY}px)`,
        }}
      />

      {/* Persistent Top Terminal Status Bar (Parallax Midlayer) */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 50,
          right: 50,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          backgroundColor: "#111827DD",
          border: "1px solid #374151",
          borderRadius: 16,
          padding: "14px 28px",
          backdropFilter: "blur(12px)",
          zIndex: 100,
          transform: `translateY(${midlayerPanY}px)`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 12px ${accentColor}`,
            }}
          />
          <span style={{ fontSize: 24, fontWeight: 800, color: "#F9FAFB", letterSpacing: 0.5 }}>
            {brandName} <span style={{ color: "#9CA3AF", fontSize: 20 }}>Terminal</span>
          </span>
        </div>

        <div style={{ fontFamily: "monospace", fontSize: 18, color: secondaryColor, fontWeight: 700 }}>
          [SYSTEM SIGNAL]
        </div>
      </div>

      {/* SCENE 1: Opening Hook / Lead */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: o1,
          transform: `scale(${0.9 + s1Spring * 0.1}) translateY(${(1 - s1Spring) * 30}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "#EF44441F",
            border: "1.5px solid #EF4444",
            color: "#EF4444",
            fontFamily: "monospace",
            fontSize: 22,
            fontWeight: 800,
            padding: "10px 24px",
            borderRadius: 8,
            marginBottom: 30,
            letterSpacing: 1.5,
          }}
        >
          HISTORICAL SIGNAL LOG // {ticker}
        </div>

        <div
          style={{
            backgroundColor: "#111827EE",
            border: "1px solid #374151",
            borderRadius: 24,
            padding: "50px 60px",
            textAlign: "center",
            maxWidth: 920,
            boxShadow: "0 25px 60px rgba(0,0,0,0.8)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 24, color: secondaryColor, marginBottom: 20 }}>
            &gt; REAL MARKET CALL DETECTED
          </div>
          <h1 style={{ fontSize: 64, fontWeight: 900, lineHeight: 1.2, color: "#F9FAFB" }}>
            PROPRIETARY SENTIMENT SIGNAL ON <span style={{ color: accentColor }}>{ticker}</span>
          </h1>
        </div>
      </div>

      {/* SCENE 2: Stat Reveal Hero Card */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: o2,
          transform: `scale(${0.88 + s2Spring * 0.12}) translateY(${(1 - s2Spring) * 25}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "#111827DD",
            border: "1.5px solid #374151",
            borderRadius: 28,
            padding: "50px 60px",
            width: "100%",
            maxWidth: 920,
            boxShadow: "0 25px 60px rgba(0,0,0,0.9)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 22, color: "#9CA3AF", marginBottom: 20 }}>
            QUANTITATIVE SETUP // {ticker}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 25 }}>
            <span style={{ fontSize: 72, fontWeight: 900, color: secondaryColor }}>{ticker}</span>
            <span
              style={{
                backgroundColor: accentColor,
                color: "#030712",
                fontSize: 48,
                fontWeight: 900,
                padding: "8px 30px",
                borderRadius: 14,
              }}
            >
              {direction}
            </span>
          </div>

          <div style={{ height: 1, backgroundColor: "#374151", margin: "25px 0" }} />

          <div style={{ display: "flex", flexDirection: "column", gap: 15 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 32 }}>
              <span style={{ color: "#9CA3AF" }}>ENTRY PRICE</span>
              <span style={{ fontWeight: 800, color: "#FFF" }}>{price}</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 36, fontWeight: 800, color: accentColor }}>
              <span>TARGET PRICE 1</span>
              <span>{target} ➔</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 28, color: "#EF4444" }}>
              <span>STOP LOSS 1</span>
              <span>{stop}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SCENE 3: Sentiment Confidence Level & Gauge */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: o3,
          transform: `scale(${0.9 + s3Spring * 0.1}) translateY(${(1 - s3Spring) * 20}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "#111827DD",
            border: "1.5px solid #374151",
            borderRadius: 28,
            padding: "50px 60px",
            textAlign: "center",
            width: "100%",
            maxWidth: 920,
            boxShadow: "0 25px 60px rgba(0,0,0,0.9)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 22, color: "#9CA3AF", marginBottom: 20 }}>
            [QUANT MODEL CONFIDENCE GAUGE]
          </div>

          <div
            style={{
              fontSize: 140,
              fontWeight: 900,
              color: accentColor,
              lineHeight: 1,
              fontFamily: "monospace",
              textShadow: `0 0 30px ${accentColor}55`,
              margin: "15px 0",
            }}
          >
            {currentConfidence}%
          </div>

          <p style={{ fontSize: 28, color: "#E5E7EB", lineHeight: 1.4, margin: "20px 0" }}>
            Strong bullish social sentiment &amp; supportive technical structure.
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "space-around",
              backgroundColor: "#1F2937",
              borderRadius: 12,
              padding: "16px 20px",
              fontFamily: "monospace",
              fontSize: 20,
              color: "#9CA3AF",
              marginTop: 20,
            }}
          >
            <span>X (30%)</span>
            <span>Groq (60%)</span>
            <span>YouTube (10%)</span>
          </div>
        </div>
      </div>

      {/* SCENE 4: Liquidity & Momentum Matrix */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: o4,
          transform: `scale(${0.9 + s4Spring * 0.1}) translateY(${(1 - s4Spring) * 20}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "#111827DD",
            border: "1.5px solid #374151",
            borderRadius: 28,
            padding: "50px 60px",
            textAlign: "center",
            maxWidth: 920,
            boxShadow: "0 25px 60px rgba(0,0,0,0.9)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 22, color: secondaryColor, marginBottom: 20 }}>
            [LIQUIDITY &amp; MOMENTUM MATRIX]
          </div>

          <h2 style={{ fontSize: 44, fontWeight: 900, color: "#F9FAFB", lineHeight: 1.3, marginBottom: 20 }}>
            SYNTHESIZING THOUSANDS OF PROFESSIONAL TRADER VIEWS
          </h2>

          <p style={{ fontSize: 28, color: "#9CA3AF", lineHeight: 1.4 }}>
            Revealing institutional liquidity positioning across platforms.
          </p>
        </div>
      </div>

      {/* SCENE 5: Call to Action / Order Execution */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: o5,
          transform: `scale(${0.85 + s5Spring * 0.15}) translateY(${(1 - s5Spring) * 20}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "#111827DD",
            border: "1.5px solid #374151",
            borderRadius: 28,
            padding: "50px 60px",
            textAlign: "center",
            maxWidth: 920,
            boxShadow: "0 25px 60px rgba(0,0,0,0.9)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 22, color: accentColor, marginBottom: 20 }}>
            &gt; EXECUTE QUANTITATIVE EDGE
          </div>

          <h2 style={{ fontSize: 48, fontWeight: 900, color: "#F9FAFB", marginBottom: 40, lineHeight: 1.2 }}>
            SPOT OPPORTUNITIES WITH DATA
          </h2>

          <div
            style={{
              backgroundColor: accentColor,
              color: "#030712",
              fontSize: 32,
              fontWeight: 900,
              padding: "26px 44px",
              borderRadius: 40,
              boxShadow: `0 15px 40px ${accentColor}77`,
              lineHeight: 1.3,
            }}
          >
            {ctaText}
          </div>
        </div>
      </div>

      {/* Audio Voiceover Element */}
      {voiceoverAudioUrl && <Audio src={staticFile(voiceoverAudioUrl)} />}
    </AbsoluteFill>
  );
};
