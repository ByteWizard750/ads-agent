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
  primaryColor = "#0F172A",
  secondaryColor = "#3B82F6",
  accentColor = "#10B981",
  textColor = "#FFFFFF",
  brandName = "CrowdWisdomTrading",
  ctaText = "Claim Your Free 7-Day Trial Now",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Progress 0 to 1
  const progress = frame / durationInFrames;

  // Spring entrance animations
  const springConfig = { damping: 12, stiffness: 100, mass: 0.8 };

  const badgeSpring = spring({ frame, fps, config: springConfig });
  const statSpring = spring({ frame: frame - 15, fps, config: springConfig });
  const meterSpring = spring({ frame: frame - 45, fps, config: springConfig });
  const ctaSpring = spring({ frame: frame - (durationInFrames - 90), fps, config: springConfig });

  // Dynamic Scene Bounded Opacities
  // Scene 1: 0 - 90 frames (0s - 3s) -> Historical Call Lead
  // Scene 2: 75 - 240 frames (2.5s - 8s) -> Stat Hero Card ($140.32 -> $144.80)
  // Scene 3: 210 - 450 frames (7s - 15s) -> Sentiment Weighting Meter
  // Scene 4: 420 - End -> CTA Call to Action

  const scene1Opacity = interpolate(frame, [0, 20, 75, 90], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scene2Opacity = interpolate(frame, [75, 95, 220, 240], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scene3Opacity = interpolate(frame, [220, 240, 420, 440], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scene4Opacity = interpolate(frame, [420, 440, durationInFrames - 5, durationInFrames], [0, 1, 1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Ticking confidence counter (0% -> 46%)
  const rawConfidenceVal = parseInt(confidence.replace("%", ""), 10) || 46;
  const currentConfidenceVal = Math.round(
    interpolate(frame, [230, 300], [0, rawConfidenceVal], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: primaryColor,
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        color: textColor,
        overflow: "hidden",
      }}
    >
      {/* Background Gradient & Animated Glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at 50% ${30 + progress * 40}%, ${secondaryColor}33 0%, transparent 70%), linear-gradient(180deg, #0F172A 0%, #020617 100%)`,
        }}
      />

      {/* Vox-Style Halftone Paper Grain Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.06,
          backgroundImage: `radial-gradient(#FFFFFF 1px, transparent 0)`,
          backgroundSize: "8px 8px",
          pointerEvents: "none",
        }}
      />

      {/* Top Header Branding Badge */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 60,
          right: 60,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 50,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "#1E293B99",
            padding: "12px 24px",
            borderRadius: 40,
            border: "1px solid #334155",
            backdropFilter: "blur(10px)",
          }}
        >
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 12px ${accentColor}`,
            }}
          />
          <span style={{ fontSize: 24, fontWeight: 700, letterSpacing: 1 }}>
            {brandName.toUpperCase()}
          </span>
        </div>

        <div
          style={{
            backgroundColor: "#EF444422",
            color: "#EF4444",
            border: "1px solid #EF4444",
            padding: "8px 18px",
            borderRadius: 20,
            fontSize: 20,
            fontWeight: 800,
            letterSpacing: 1.5,
          }}
        >
          HISTORICAL SIGNAL
        </div>
      </div>

      {/* SCENE 1: Historical Call Lead */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
          opacity: scene1Opacity,
          transform: `scale(${0.9 + badgeSpring * 0.1})`,
        }}
      >
        <div
          style={{
            backgroundColor: "#FFF",
            color: "#000",
            fontSize: 32,
            fontWeight: 900,
            padding: "12px 28px",
            transform: "rotate(-2deg)",
            boxShadow: "8px 8px 0px #EF4444",
            marginBottom: 40,
            letterSpacing: 2,
          }}
        >
          REAL MARKET CALL
        </div>
        <h1
          style={{
            fontSize: 76,
            fontWeight: 900,
            textAlign: "center",
            lineHeight: 1.1,
            textTransform: "uppercase",
            textShadow: "0 10px 30px rgba(0,0,0,0.5)",
          }}
        >
          SENSING PROPRIETARY SENTIMENT SHIFTS
        </h1>
      </div>

      {/* SCENE 2: Stat Hero Cards (SNOW LONG $140.32 -> $144.80) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: scene2Opacity,
          transform: `scale(${0.85 + statSpring * 0.15})`,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 20,
            alignItems: "center",
            marginBottom: 30,
          }}
        >
          <div
            style={{
              backgroundColor: secondaryColor,
              color: "#FFF",
              fontSize: 48,
              fontWeight: 900,
              padding: "12px 32px",
              borderRadius: 16,
            }}
          >
            {ticker}
          </div>
          <div
            style={{
              backgroundColor: accentColor,
              color: "#000",
              fontSize: 48,
              fontWeight: 900,
              padding: "12px 32px",
              borderRadius: 16,
            }}
          >
            {direction}
          </div>
        </div>

        {/* Hero Stat Box */}
        <div
          style={{
            backgroundColor: "#1E293BE6",
            border: "2px solid #334155",
            borderRadius: 32,
            padding: "40px 60px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
            position: "relative",
          }}
        >
          <span style={{ fontSize: 28, color: "#94A3B8", fontWeight: 600 }}>
            ENTRY PRICE
          </span>
          <span style={{ fontSize: 96, fontWeight: 900, color: "#FFF", margin: "10px 0" }}>
            {price}
          </span>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              marginTop: 10,
              color: accentColor,
              fontSize: 40,
              fontWeight: 800,
            }}
          >
            <span>TARGET: {target}</span>
            <span style={{ fontSize: 50 }}>➔</span>
          </div>
          <div style={{ marginTop: 15, fontSize: 24, color: "#EF4444", fontWeight: 700 }}>
            STOP LOSS: {stop}
          </div>
        </div>
      </div>

      {/* SCENE 3: Ticking Sentiment Confidence Meter */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: scene3Opacity,
          transform: `scale(${0.9 + meterSpring * 0.1})`,
        }}
      >
        <span
          style={{
            fontSize: 32,
            fontWeight: 800,
            color: "#94A3B8",
            letterSpacing: 2,
            marginBottom: 20,
          }}
        >
          SENTIMENT CONFIDENCE SCORE
        </span>

        <div
          style={{
            fontSize: 160,
            fontWeight: 900,
            color: accentColor,
            lineHeight: 1,
            textShadow: `0 0 40px ${accentColor}66`,
          }}
        >
          {currentConfidenceVal}%
        </div>

        <p
          style={{
            fontSize: 32,
            textAlign: "center",
            color: "#E2E8F0",
            maxWidth: 800,
            marginTop: 30,
            lineHeight: 1.4,
          }}
        >
          Synthesized across <b>X (30%)</b>, <b>Groq (60%)</b> & <b>YouTube</b> sentiment streams.
        </p>
      </div>

      {/* SCENE 4: Call to Action (CTA) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: scene4Opacity,
          transform: `scale(${0.85 + ctaSpring * 0.15})`,
        }}
      >
        <div
          style={{
            fontSize: 54,
            fontWeight: 900,
            textAlign: "center",
            marginBottom: 50,
            lineHeight: 1.2,
          }}
        >
          TRADE WITH STATISTICAL EDGE
        </div>

        <div
          style={{
            backgroundColor: accentColor,
            color: "#0F172A",
            fontSize: 40,
            fontWeight: 900,
            padding: "32px 64px",
            borderRadius: 60,
            textAlign: "center",
            boxShadow: `0 15px 40px ${accentColor}88`,
            letterSpacing: 1,
            transform: `scale(${1 + Math.sin(frame / 10) * 0.03})`,
          }}
        >
          {ctaText.toUpperCase()}
        </div>
      </div>

      {/* Audio Voiceover Element */}
      {voiceoverAudioUrl && <Audio src={staticFile(voiceoverAudioUrl)} />}
    </AbsoluteFill>
  );
};
