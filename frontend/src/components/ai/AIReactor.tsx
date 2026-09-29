import React from "react";

export type ReactorState =
  | "IDLE"
  | "SCANNING"
  | "ANALYZING"
  | "MATCHING"
  | "PREPARING"
  | "APPLYING"
  | "COMPLETE"
  | "ERROR";

interface AIReactorProps {
  state?: ReactorState;
  size?: number | "sm" | "md" | "lg";
  className?: string;
  showStatusLabel?: boolean;
}

const sizeMap = {
  sm: 180,
  md: 280,
  lg: 380,
};

export const AIReactor: React.FC<AIReactorProps> = ({
  state = "IDLE",
  size = "md",
  className = "",
  showStatusLabel = false,
}) => {
  const pixelSize = typeof size === "number" ? size : sizeMap[size] || 280;
  const isError = state === "ERROR";
  const isComplete = state === "COMPLETE";

  // Palette based on reactor state
  const colors = isError
    ? {
        primary: "#EF4444",
        secondary: "#B91C1C",
        deep: "#450A0A",
        glow: "rgba(239, 68, 68, 0.6)",
        accent: "#FCA5A5",
      }
    : {
        primary: "#FFB400", // Amber
        secondary: "#FF8A00", // Orange
        deep: "#993300", // Dark Orange
        deepest: "#1A0000",
        glow: "rgba(255, 180, 0, 0.5)",
        accent: "#FFFFFF",
      };

  // State-specific animation speeds and styles
  const getSpeedClass = () => {
    switch (state) {
      case "SCANNING":
        return {
          outer: "animate-spin-mid",
          middle: "animate-spin-reverse",
          inner: "animate-spin-slow",
          pulse: "animate-pulse-energy",
        };
      case "ANALYZING":
        return {
          outer: "animate-spin-slow",
          middle: "animate-spin-mid",
          inner: "animate-spin-reverse-fast",
          pulse: "animate-pulse-energy",
        };
      case "MATCHING":
        return {
          outer: "animate-spin-mid",
          middle: "animate-spin-reverse-fast",
          inner: "animate-spin-mid",
          pulse: "animate-pulse-energy",
        };
      case "PREPARING":
      case "APPLYING":
        return {
          outer: "animate-spin-mid",
          middle: "animate-spin-reverse",
          inner: "animate-spin-reverse-fast",
          pulse: "animate-pulse-energy",
        };
      case "COMPLETE":
        return {
          outer: "opacity-60",
          middle: "opacity-70",
          inner: "opacity-80",
          pulse: "",
        };
      case "ERROR":
        return {
          outer: "",
          middle: "animate-spin-slow",
          inner: "",
          pulse: "animate-pulse-energy",
        };
      case "IDLE":
      default:
        return {
          outer: "animate-spin-slow",
          middle: "animate-spin-reverse",
          inner: "animate-spin-slow",
          pulse: "animate-pulse-energy",
        };
    }
  };

  const speed = getSpeedClass();

  return (
    <div
      className={`relative inline-flex flex-col items-center justify-center select-none ${className}`}
      style={{ width: pixelSize, height: pixelSize }}
      aria-label={`AI Reactor - State: ${state}`}
    >
      <svg
        viewBox="0 0 400 400"
        className="w-full h-full overflow-visible"
        aria-hidden="true"
      >
        <defs>
          {/* Radial glow for nucleus */}
          <radialGradient id={`reactor-glow-${state}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={colors.primary} stopOpacity={state === "APPLYING" ? "1" : "0.85"} />
            <stop offset="45%" stopColor={colors.secondary} stopOpacity="0.5" />
            <stop offset="100%" stopColor={colors.deep} stopOpacity="0" />
          </radialGradient>

          {/* Core nucleus gradient */}
          <radialGradient id={`core-grad-${state}`} cx="40%" cy="40%" r="60%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="35%" stopColor={colors.primary} />
            <stop offset="75%" stopColor={colors.secondary} />
            <stop offset="100%" stopColor={colors.deep} />
          </radialGradient>

          <filter id="glow-blur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* BACKGROUND: Structural Crosshairs & Coordinate Grids */}
        <g stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1">
          <line x1="200" y1="20" x2="200" y2="380" strokeDasharray="3 6" />
          <line x1="20" y1="200" x2="380" y2="200" strokeDasharray="3 6" />
          <circle cx="200" cy="200" r="185" fill="none" stroke="rgba(255, 138, 0, 0.04)" strokeWidth="1" />
        </g>

        {/* OUTER LAYER: Large Orbital Track & Peripheral Satellites */}
        <g className={`origin-center ${speed.outer}`}>
          {/* Outer elliptical ring with tick marks */}
          <circle
            cx="200"
            cy="200"
            r="165"
            fill="none"
            stroke={colors.deep}
            strokeWidth="1.2"
            strokeDasharray="6 14"
            opacity="0.6"
          />
          <circle
            cx="200"
            cy="200"
            r="150"
            fill="none"
            stroke={colors.secondary}
            strokeWidth="1"
            strokeDasharray="24 120"
            opacity="0.75"
          />

          {/* Peripheral satellite nodes */}
          <circle cx="200" cy="35" r="3.5" fill={colors.primary} />
          <circle cx="365" cy="200" r="3.5" fill={colors.secondary} />
          <circle cx="200" cy="365" r="3.5" fill={colors.primary} />
          <circle cx="35" cy="200" r="3.5" fill={colors.secondary} />

          {/* Micro ticks at cardinal quadrants */}
          <path
            d="M196 35 h8 M365 196 v8 M196 365 h8 M35 196 v8"
            stroke={colors.primary}
            strokeWidth="1.5"
          />
        </g>

        {/* MIDDLE LAYER: Dynamic Energy Traces & Segmented Arcs */}
        <g className={`origin-center ${speed.middle}`}>
          {/* Active energy stream */}
          <circle
            cx="200"
            cy="200"
            r="115"
            fill="none"
            stroke={colors.primary}
            strokeWidth="2"
            strokeDasharray={state === "MATCHING" || state === "APPLYING" ? "45 35 15 25" : "30 70"}
            strokeLinecap="round"
            className="animate-dash-flow"
            filter="url(#glow-blur)"
          />

          <circle
            cx="200"
            cy="200"
            r="105"
            fill="none"
            stroke={colors.secondary}
            strokeWidth="1"
            strokeDasharray="12 18"
            opacity="0.6"
          />

          {/* Orbiting data packets */}
          <circle cx="200" cy="85" r="3" fill="#FFFFFF" filter="url(#glow-blur)" />
          <circle cx="290" cy="250" r="2.5" fill={colors.primary} />
          <circle cx="110" cy="250" r="2.5" fill={colors.secondary} />
        </g>

        {/* INNER LAYER: Mechanical Shutter & Aperture Ring */}
        <g className={`origin-center ${speed.inner}`}>
          <circle
            cx="200"
            cy="200"
            r="70"
            fill="none"
            stroke={colors.secondary}
            strokeWidth="1.5"
            strokeDasharray="4 8"
            opacity="0.8"
          />
          {/* Notched mechanical teeth */}
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <line
              key={deg}
              x1="200"
              y1="134"
              x2="200"
              y2="140"
              stroke={colors.primary}
              strokeWidth="2"
              transform={`rotate(${deg} 200 200)`}
            />
          ))}
        </g>

        {/* CENTER NUCLEUS: Glowing Energy Core */}
        <g className={`origin-center ${speed.pulse}`}>
          {/* Ambient radial glow halo */}
          <circle
            cx="200"
            cy="200"
            r={state === "APPLYING" || state === "PREPARING" ? "55" : "45"}
            fill={`url(#reactor-glow-${state})`}
          />

          {/* Hard containment ring */}
          <circle
            cx="200"
            cy="200"
            r="28"
            fill="#050505"
            stroke={colors.primary}
            strokeWidth="2"
            filter="url(#glow-blur)"
          />

          {/* Solid core orb */}
          <circle
            cx="200"
            cy="200"
            r={state === "COMPLETE" ? "18" : "14"}
            fill={`url(#core-grad-${state})`}
          />

          {/* Visual completion check or central singularity */}
          {isComplete ? (
            <path
              d="M193 200 l5 5 l10 -10"
              fill="none"
              stroke="#050505"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ) : (
            <circle cx="198" cy="198" r="3" fill="#FFFFFF" opacity="0.9" />
          )}
        </g>
      </svg>

      {/* Optional technical HUD readout underneath */}
      {showStatusLabel && (
        <div className="mt-2 flex flex-col items-center gap-0.5">
          <div className="flex items-center gap-1.5">
            <span
              className={`inline-block w-1.5 h-1.5 rounded-full ${
                isError ? "bg-red-500 animate-ping" : "bg-[#FFB400] animate-pulse"
              }`}
            />
            <span className="font-mono text-[10px] tracking-widest text-[#FFB400] font-semibold uppercase">
              REACTOR // {state}
            </span>
          </div>
          <span className="font-mono text-[9px] text-[#6B7280] tracking-wider uppercase">
            ORBITAL HARMONIC 440HZ
          </span>
        </div>
      )}
    </div>
  );
};
export default AIReactor;
