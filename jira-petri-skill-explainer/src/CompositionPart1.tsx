import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import React from "react";

const TitleSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const titleScale = interpolate(frame, [0, 30], [0.8, 1], { extrapolateRight: "clamp" });
  const subtitleOpacity = interpolate(frame - 20, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0a1628 0%, #1a2744 100%)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{ transform: `scale(${titleScale})`, textAlign: "center" }}>
        <h1 style={{ fontSize: 52, color: "#e8e8e8", margin: 0, fontWeight: 300, letterSpacing: "2px" }}>Petri Net Workflow Analysis</h1>
        <p style={{ fontSize: 22, color: "#64b5f6", margin: "20px 0", opacity: subtitleOpacity, fontWeight: 300 }}>Formal Verification of Ticket-Based Systems</p>
        <div style={{ marginTop: 30, fontSize: 13, color: "#8899a6" }}>Educational Research Project • Apache 2.0 License</div>
      </div>
    </AbsoluteFill>
  );
};

const MotivationSlide: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%)", padding: 60 }}>
      <h2 style={{ fontSize: 38, color: "#e8e8e8", textAlign: "center", marginBottom: 35, fontWeight: 400 }}>Research Motivation</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 22, maxWidth: 900, margin: "0 auto" }}>
        {[{ icon: "🔗", title: "Complex Dependencies", desc: "Multi-ticket blocking chains create emergent behavior", color: "#64b5f6" }, { icon: "👥", title: "Shared Resources", desc: "Contention for reviewers, environments, databases", color: "#4fc3f7" }, { icon: "📊", title: "Emergent Bottlenecks", desc: "Queue accumulation not visible from individual tickets", color: "#26c6da" }, { icon: "⚠️", title: "Systemic Deadlocks", desc: "Circular dependencies halt entire workflows", color: "#ef5350" }].map((item, index) => {
          const opacity = interpolate(frame - index * 10, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (<div key={index} style={{ background: "rgba(100, 181, 246, 0.08)", border: `1px solid ${item.color}40`, borderRadius: 8, padding: "22px 26px", opacity }}><div style={{ fontSize: 28, marginBottom: 10 }}>{item.icon}</div><div style={{ fontSize: 18, color: item.color, fontWeight: 500, marginBottom: 8 }}>{item.title}</div><div style={{ fontSize: 13, color: "#b0bec5", lineHeight: 1.5 }}>{item.desc}</div></div>);
        })}
      </div>
      <div style={{ textAlign: "center", marginTop: 30, fontSize: 12, color: "#546e7a" }}>Non-commercial educational project • Created for research and learning purposes</div>
    </AbsoluteFill>
  );
};

export { TitleSlide, MotivationSlide };