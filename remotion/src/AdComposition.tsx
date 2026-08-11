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
  ctaText = "Claim your free 7-day trial of CrowdWisdomTrading signals now",
  designVariant = "option2_editorial",
  scenes,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Define default dynamic scene frame boundaries if scenes prop is omitted
  const sLeadStart = scenes?.[0]?.startFrame ?? 0;
  const sLeadEnd = scenes?.[0]?.endFrame ?? 150;
  const sStatStart = scenes?.[1]?.startFrame ?? 150;
  const sStatEnd = scenes?.[1]?.endFrame ?? 290;
  const sConfStart = scenes?.[2]?.startFrame ?? 290;
  const sConfEnd = scenes?.[2]?.endFrame ?? 608;
  const sTraderStart = scenes?.[3]?.startFrame ?? 608;
  const sTraderEnd = scenes?.[3]?.endFrame ?? 860;
  const sCtaStart = scenes?.[4]?.startFrame ?? 860;
  const sCtaEnd = scenes?.[4]?.endFrame ?? (durationInFrames || 1102);

  // Spring entrance animations
  const springConfig = { damping: 12, stiffness: 100, mass: 0.8 };
  const leadSpring = spring({ frame: frame - sLeadStart, fps, config: springConfig });
  const statSpring = spring({ frame: frame - sStatStart, fps, config: springConfig });
  const confSpring = spring({ frame: frame - sConfStart, fps, config: springConfig });
  const traderSpring = spring({ frame: frame - sTraderStart, fps, config: springConfig });
  const ctaSpring = spring({ frame: frame - sCtaStart, fps, config: springConfig });

  // Opacity interpolations for synchronized visual beats
  const leadOpacity = interpolate(frame, [sLeadStart, sLeadStart + 15, sLeadEnd - 15, sLeadEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const statOpacity = interpolate(frame, [sStatStart, sStatStart + 15, sStatEnd - 15, sStatEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const confOpacity = interpolate(frame, [sConfStart, sConfStart + 15, sConfEnd - 15, sConfEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const traderOpacity = interpolate(frame, [sTraderStart, sTraderStart + 15, sTraderEnd - 15, sTraderEnd], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ctaOpacity = interpolate(frame, [sCtaStart, sCtaStart + 15, durationInFrames - 5, durationInFrames], [0, 1, 1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Ticking confidence counter (0% -> 46%)
  const rawConfidenceVal = parseInt(confidence.replace("%", ""), 10) || 46;
  const currentConfidenceVal = Math.round(
    interpolate(frame, [sConfStart + 15, sConfStart + 75], [0, rawConfidenceVal], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  // Render option 1: Clean Stat Reveal
  if (designVariant === "option1_stat_reveal") {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#0B132B",
          fontFamily: "'Inter', system-ui, sans-serif",
          color: "#FFFFFF",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle at 50% 40%, #1C2541 0%, #0B132B 100%)" }} />
        {/* Top Header Badge */}
        <div style={{ position: "absolute", top: 80, left: 60, right: 60, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#48CAE4", letterSpacing: 1 }}>{brandName}</div>
          <div style={{ backgroundColor: "#1C2541", border: "1px solid #48CAE4", color: "#48CAE4", padding: "8px 20px", borderRadius: 20, fontSize: 18, fontWeight: 700 }}>
            HISTORICAL CALL
          </div>
        </div>

        {/* Scene: Stat Reveal Hero */}
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, opacity: Math.max(statOpacity, 0.9) }}>
          <div style={{ backgroundColor: "#1C2541EE", border: "2px solid #48CAE4", borderRadius: 32, padding: "50px 70px", display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "0 25px 60px rgba(0,0,0,0.6)" }}>
            <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
              <span style={{ backgroundColor: "#0077B6", color: "#FFF", fontSize: 44, fontWeight: 900, padding: "10px 28px", borderRadius: 12 }}>{ticker}</span>
              <span style={{ backgroundColor: "#52B788", color: "#000", fontSize: 44, fontWeight: 900, padding: "10px 28px", borderRadius: 12 }}>{direction}</span>
            </div>
            <span style={{ fontSize: 26, color: "#90E0EF", fontWeight: 600 }}>ENTRY PRICE</span>
            <span style={{ fontSize: 100, fontWeight: 900, color: "#FFF", margin: "10px 0" }}>{price}</span>
            <div style={{ fontSize: 42, color: "#52B788", fontWeight: 800 }}>TARGET: {target} ➔</div>
            <div style={{ fontSize: 24, color: "#E63946", fontWeight: 700, marginTop: 15 }}>STOP: {stop}</div>
          </div>
        </div>
        {voiceoverAudioUrl && <Audio src={staticFile(voiceoverAudioUrl)} />}
      </AbsoluteFill>
    );
  }

  // Render option 3: Quantitative Trading Terminal
  if (designVariant === "option3_terminal") {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#030712",
          fontFamily: "'Inter', monospace, sans-serif",
          color: "#F9FAFB",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(#111827 1px, transparent 1px), linear-gradient(90deg, #111827 1px, transparent 1px)", backgroundSize: "40px 40px", opacity: 0.4 }} />
        {/* Terminal Header */}
        <div style={{ position: "absolute", top: 80, left: 60, right: 60, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#10B981" }} />
            <span style={{ fontSize: 26, fontWeight: 800, color: "#F9FAFB" }}>{brandName} Terminal</span>
          </div>
          <span style={{ color: "#3B82F6", fontSize: 20, fontFamily: "monospace" }}>[SYSTEM SIGNAL]</span>
        </div>

        {/* Hero Card */}
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: 60, opacity: Math.max(statOpacity, 0.9) }}>
          <div style={{ backgroundColor: "#111827DD", border: "1px solid #374151", borderRadius: 24, padding: "50px 60px", width: "100%", maxWidth: 900, backdropFilter: "blur(20px)", boxShadow: "0 20px 50px rgba(0,0,0,0.8)" }}>
            <div style={{ fontSize: 22, color: "#9CA3AF", marginBottom: 20, textTransform: "uppercase" }}>QUANTITATIVE SETUP // {ticker}</div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 30 }}>
              <span style={{ fontSize: 84, fontWeight: 900, color: "#10B981" }}>{direction}</span>
              <span style={{ fontSize: 64, fontWeight: 800 }}>{price}</span>
            </div>
            <div style={{ height: 2, backgroundColor: "#374151", margin: "20px 0" }} />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 32, fontWeight: 700 }}>
              <span style={{ color: "#9CA3AF" }}>TARGET: <b style={{ color: "#10B981" }}>{target}</b></span>
              <span style={{ color: "#9CA3AF" }}>CONFIDENCE: <b style={{ color: "#3B82F6" }}>{confidence}</b></span>
            </div>
          </div>
        </div>
        {voiceoverAudioUrl && <Audio src={staticFile(voiceoverAudioUrl)} />}
      </AbsoluteFill>
    );
  }

  // Render option 2: Editorial / Newspaper Diorama (Default)
  return (
    <AbsoluteFill
      style={{
        backgroundColor: primaryColor,
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        color: textColor,
        overflow: "hidden",
      }}
    >
      {/* Background Gradient */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at 50% 40%, ${secondaryColor}33 0%, transparent 70%), linear-gradient(180deg, #0F172A 0%, #020617 100%)`,
        }}
      />

      {/* Vox-Style Halftone Print Texture Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.08,
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
            gap: 14,
            backgroundColor: "#1E293BCC",
            padding: "12px 28px",
            borderRadius: 40,
            border: "1px solid #334155",
            backdropFilter: "blur(10px)",
          }}
        >
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 10px ${accentColor}`,
            }}
          />
          <span style={{ fontSize: 26, fontWeight: 800, color: "#FFFFFF", letterSpacing: 0.5 }}>
            {brandName}
          </span>
        </div>

        <div
          style={{
            backgroundColor: "#EF444422",
            color: "#EF4444",
            border: "1.5px solid #EF4444",
            padding: "8px 20px",
            borderRadius: 20,
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 1,
          }}
        >
          HISTORICAL CALL
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
          opacity: leadOpacity,
          transform: `scale(${0.9 + leadSpring * 0.1})`,
        }}
      >
        <div
          style={{
            backgroundColor: "#F8FAFC",
            color: "#0F172A",
            fontSize: 34,
            fontWeight: 900,
            padding: "12px 30px",
            transform: "rotate(-2deg)",
            boxShadow: "8px 8px 0px #EF4444",
            marginBottom: 40,
            letterSpacing: 1.5,
          }}
        >
          HERE'S A REAL CALL WE MADE
        </div>
        <h1
          style={{
            fontSize: 72,
            fontWeight: 900,
            textAlign: "center",
            lineHeight: 1.15,
            textTransform: "uppercase",
            color: "#FFFFFF",
          }}
        >
          PROPRIETARY SENTIMENT SIGNAL ON <span style={{ color: secondaryColor }}>{ticker}</span>
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
          opacity: statOpacity,
          transform: `scale(${0.85 + statSpring * 0.15})`,
        }}
      >
        <div style={{ display: "flex", gap: 20, marginBottom: 30 }}>
          <div style={{ backgroundColor: secondaryColor, color: "#FFF", fontSize: 44, fontWeight: 900, padding: "12px 32px", borderRadius: 16 }}>
            {ticker}
          </div>
          <div style={{ backgroundColor: accentColor, color: "#000", fontSize: 44, fontWeight: 900, padding: "12px 32px", borderRadius: 16 }}>
            {direction}
          </div>
        </div>

        <div style={{ backgroundColor: "#1E293BE6", border: "2px solid #334155", borderRadius: 32, padding: "40px 60px", display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "0 20px 50px rgba(0,0,0,0.5)" }}>
          <span style={{ fontSize: 26, color: "#94A3B8", fontWeight: 600 }}>ENTRY PRICE</span>
          <span style={{ fontSize: 96, fontWeight: 900, color: "#FFF", margin: "10px 0" }}>{price}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 10, color: accentColor, fontSize: 40, fontWeight: 800 }}>
            <span>TARGET: {target}</span>
            <span style={{ fontSize: 48 }}>➔</span>
          </div>
          <div style={{ marginTop: 15, fontSize: 24, color: "#EF4444", fontWeight: 700 }}>
            STOP LOSS: {stop}
          </div>
        </div>
      </div>

      {/* SCENE 3: Ticking Sentiment Confidence Score */}
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
        <span style={{ fontSize: 30, fontWeight: 800, color: "#94A3B8", letterSpacing: 2, marginBottom: 20 }}>
          CONFIDENCE LEVEL
        </span>
        <div style={{ fontSize: 160, fontWeight: 900, color: accentColor, lineHeight: 1, textShadow: `0 0 40px ${accentColor}66` }}>
          {currentConfidenceVal}%
        </div>
        <p style={{ fontSize: 32, textAlign: "center", color: "#E2E8F0", maxWidth: 800, marginTop: 30, lineHeight: 1.4 }}>
          Strong bullish social sentiment & supportive technical structure.
        </p>
      </div>

      {/* SCENE 4: Trader Consensus & Liquidity */}
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
        <div style={{ backgroundColor: "#1E293BCC", border: "1px solid #334155", borderRadius: 28, padding: "50px 60px", textAlign: "center", maxWidth: 900 }}>
          <h2 style={{ fontSize: 48, fontWeight: 900, color: secondaryColor, marginBottom: 20 }}>
            SYNTHESIZING THOUSANDS OF TRADER VIEWS
          </h2>
          <p style={{ fontSize: 30, color: "#E2E8F0", lineHeight: 1.4 }}>
            Revealing where liquidity and momentum build across platforms.
          </p>
        </div>
      </div>

      {/* SCENE 5: Call to Action (CTA) */}
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
        <div style={{ fontSize: 50, fontWeight: 900, textAlign: "center", marginBottom: 50, lineHeight: 1.2 }}>
          SPOT OPPORTUNITIES WITH DATA
        </div>
        <div
          style={{
            backgroundColor: accentColor,
            color: "#0F172A",
            fontSize: 34,
            fontWeight: 900,
            padding: "28px 50px",
            borderRadius: 50,
            textAlign: "center",
            boxShadow: `0 15px 40px ${accentColor}88`,
            lineHeight: 1.3,
          }}
        >
          {ctaText}
        </div>
      </div>

      {/* Audio Voiceover Element */}
      {voiceoverAudioUrl && <Audio src={staticFile(voiceoverAudioUrl)} />}
    </AbsoluteFill>
  );
};
