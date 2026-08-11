export interface SceneTiming {
  name: string;
  startFrame: number;
  endFrame: number;
}

export interface AdCompositionProps {
  ticker?: string;
  direction?: string;
  price?: string;
  target?: string;
  stop?: string;
  confidence?: string;
  headlineText?: string;
  fullScriptText?: string;
  voiceoverAudioUrl?: string;
  primaryColor?: string;
  secondaryColor?: string;
  accentColor?: string;
  textColor?: string;
  brandName?: string;
  ctaText?: string;
  designVariant?: "option1_stat_reveal" | "option2_editorial" | "option3_terminal";
  durationInFrames?: number;
  scenes?: SceneTiming[];
}
