export interface SubtitleWord {
  word: string;
  start_sec: number;
  end_sec: number;
}

export interface AdCompositionProps {
  ticker: string;
  direction: string;
  price: string;
  target: string;
  stop: string;
  confidence: string;
  headlineText: string;
  fullScriptText: string;
  voiceoverAudioUrl: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  textColor: string;
  brandName: string;
  ctaText: string;
  words?: SubtitleWord[];
}
