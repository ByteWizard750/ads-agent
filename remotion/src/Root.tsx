import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
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
  fullScriptText: "Here's a real call we made: Our proprietary sentiment signal on SNOW identified a LONG opportunity.",
  voiceoverAudioUrl: "voiceover.mp3",
  primaryColor: "#0F172A",
  secondaryColor: "#3B82F6",
  accentColor: "#10B981",
  textColor: "#FFFFFF",
  brandName: "CrowdWisdomTrading",
  ctaText: "Claim your free 7-day trial of CrowdWisdomTrading signals now",
  designVariant: "option2_editorial",
  durationInFrames: 1102,
};

const calculateMetadata: CalculateMetadataFunction<AdCompositionProps> = ({ props }) => {
  const durationInFrames = props.durationInFrames || 1102;
  return {
    durationInFrames,
    fps: 30,
    width: 1080,
    height: 1920,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AdComposition"
        component={AdComposition}
        durationInFrames={1102}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
        calculateMetadata={calculateMetadata}
      />
    </>
  );
};
