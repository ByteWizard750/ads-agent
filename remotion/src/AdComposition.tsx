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

  // Dynamic scene frame boundaries
  const sLeadStart = scenes?.[0]?.startFrame ?? 0;
  const sLeadEnd = scenes?.[0]?.endFrame ?? 288;
  const sStatStart = scenes?.[1]?.startFrame ?? 288;
  const sStatEnd = scenes?.[1]?.endFrame ?? 606;
  const sConfStart = scenes?.[2]?.startFrame ?? 606;
  const sConfEnd = scenes?.[2]?.endFrame ?? 858;
  const sTraderStart = scenes?.[3]?.startFrame ?? 858;
  const sTraderEnd = scenes?.[3]?.endFrame ?? 973;
  const sCtaStart = scenes?.[4]?.startFrame ?? 973;
  const sCtaEnd = scenes?.[4]?.endFrame ?? (durationInFrames || 1102);

  // Spring entrance animations
  const springConfig = { damping: 14, stiffness: 120, mass: 0.8 };
  const leadSpring = spring({ frame: frame - sLeadStart, fps, config: springConfig });
  const statSpring = spring({ frame: frame - sStatStart, fps, config: springConfig });
  const confSpring = spring({ frame: frame - sConfStart, fps, config: springConfig });
  const traderSpring = spring({ frame: frame - sTraderStart, fps, config: springConfig });
  const ctaSpring = spring({ frame: frame - sCtaStart, fps, config: springConfig });

  // Opacity interpolations across terminal scenes
  const leadOpacity = interpolate(frame, [sLeadStart, sLeadStart + 15, sLeadEnd - 15, sLeadEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const statOpacity = interpolate(frame, [sStatStart, sStatStart + 15, sStatEnd - 15, sStatEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const confOpacity = interpolate(frame, [sConfStart, sConfStart + 15, sConfEnd - 15, sConfEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const traderOpacity = interpolate(frame, [sTraderStart, sTraderStart + 15, sTraderEnd - 15, sTraderEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ctaOpacity = interpolate(frame, [sCtaStart, sCtaStart + 15, durationInFrames - 5, durationInFrames], [0, 1, 1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Digital ticking confidence counter (0% -> 46%)
  const rawConfidenceVal = parseInt(confidence.replace("%", ""), 10) || 46;
  const currentConfidenceVal = Math.round(
    interpolate(frame, [sConfStart + 15, sConfStart + 60], [0, rawConfidenceVal], {
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
      {/* Terminal Grid Background Lines */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: "linear-gradient(#111827 1px, transparent 1px), linear-gradient(90deg, #111827 1px, transparent 1px)",
          backgroundSize: "40px 40px",
          opacity: 0.45,
        }}
      />

      {/* Persistent Terminal Header Bar */}
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
          backdropFilter: "blur(10px)",
          zIndex: 100,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 10px ${accentColor}`,
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

      {/* SCENE 1: Historical Lead / System Alert */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: leadOpacity,
          transform: `scale(${0.9 + leadSpring * 0.1})`,
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
            boxShadow: "0 20px 50px rgba(0,0,0,0.8)",
          }}
        >
          <div style={{ fontFamily: "monospace", fontSize: 24, color: secondaryColor, marginBottom: 20 }}>
            &gt; REAL MARKET CALL DETECTED
          </div>
          <h1
            style={{
              fontSize: 64,
              fontWeight: 900,
              lineHeight: 1.2,
              color: "#F9FAFB",
            }}
          >
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
          opacity: statOpacity,
          transform: `scale(${0.85 + statSpring * 0.15})`,
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
          opacity: confOpacity,
          transform: `scale(${0.9 + confSpring * 0.1})`,
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
            {currentConfidenceVal}%
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
          opacity: traderOpacity,
          transform: `scale(${0.9 + traderSpring * 0.1})`,
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

      {/* SCENE 5: Call to Action (CTA) / Order Execution */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          opacity: ctaOpacity,
          transform: `scale(${0.85 + ctaSpring * 0.15})`,
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
