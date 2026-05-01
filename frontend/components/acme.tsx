import type {IconSvgProps} from "./types";

import React from "react";

export const InductifyIcon: React.FC<IconSvgProps> = ({size = 32, width, height, ...props}) => (
  <svg fill="none" height={size || height} viewBox="0 0 32 32" width={size || width} {...props}>
    {/* Top circle — the "conclusion" drawn by inductive reasoning */}
    <circle cx="16" cy="6" r="4.5" fill="currentColor" />
    {/* Trunk */}
    <path d="M16 10.5 L16 19" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    {/* Left branch */}
    <path d="M16 19 L7 27" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    {/* Right branch */}
    <path d="M16 19 L25 27" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    {/* Junction node */}
    <circle cx="16" cy="19" r="2.5" fill="currentColor" />
    {/* Leaf nodes */}
    <circle cx="7" cy="27" r="3" fill="currentColor" />
    <circle cx="25" cy="27" r="3" fill="currentColor" />
  </svg>
);
