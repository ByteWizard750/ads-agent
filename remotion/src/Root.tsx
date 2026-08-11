import React from "react";
import { Composition } from "remotion";
import { AdComposition } from "./AdComposition";
import { AdCompositionProps } from "./types";
import "./index.css";

const defaultProps: AdCompositionProps = {
  ticker: "SNOW",
  direction: "LONG",
  price: "$140.32",
  target: "$144.80",
  stop: "$137.20",
  confidence: "46%",
  headlineText: "Here's a real call we made on SNOW",
  fullScriptText: "Here's a real call we made: Our proprietary sentiment signal on SNOW identified a LONG opportunity at $140.32 targeting $144.80.",
  voiceoverAudioUrl: "voiceover.mp3",
  primaryColor: "#0F172A",
  secondaryColor: "#3B82F6",
  accentColor: "#10B981",
  textColor: "#FFFFFF",
  brandName: "CrowdWisdomTrading",
  ctaText: "Claim Your Free 7-Day Trial Now",
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AdComposition"
        component={AdComposition}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
    </>
  );
};
