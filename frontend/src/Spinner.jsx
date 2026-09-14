// A small, dependency-free loading indicator. Generative answers can take
// several seconds (the Gemini path measured ~8.3s in practice), so a
// spinner + rotating status text is worth the little bit of code -- a bare
// "Asking..." button label reads as frozen over that long a wait.
import { useEffect, useState } from "react";

const STAGES = [
  "Retrieving relevant passages…",
  "Reading regulations and near-miss reports…",
  "Reasoning over retrieved context…",
  "Still working — generative answers can take a few seconds…",
];

export default function Spinner() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, STAGES.length - 1));
    }, 1800);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="spinner-row" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span className="spinner-label">{STAGES[stageIndex]}</span>
    </div>
  );
}
