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
        {[
          { icon: "🔗", title: "Complex Dependencies", desc: "Multi-ticket blocking chains create emergent behavior", color: "#64b5f6" },
          { icon: "👥", title: "Shared Resources", desc: "Contention for reviewers, environments, databases", color: "#4fc3f7" },
          { icon: "📊", title: "Emergent Bottlenecks", desc: "Queue accumulation not visible from individual tickets", color: "#26c6da" },
          { icon: "⚠️", title: "Systemic Deadlocks", desc: "Circular dependencies halt entire workflows", color: "#ef5350" },
        ].map((item, index) => {
          const opacity = interpolate(frame - index * 10, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={index} style={{ background: "rgba(100, 181, 246, 0.08)", border: `1px solid ${item.color}40`, borderRadius: 8, padding: "22px 26px", opacity }}>
              <div style={{ fontSize: 28, marginBottom: 10 }}>{item.icon}</div>
              <div style={{ fontSize: 18, color: item.color, fontWeight: 500, marginBottom: 8 }}>{item.title}</div>
              <div style={{ fontSize: 13, color: "#b0bec5", lineHeight: 1.5 }}>{item.desc}</div>
            </div>
          );
        })}
      </div>
      <div style={{ textAlign: "center", marginTop: 30, fontSize: 12, color: "#546e7a" }}>Non-commercial educational project • Created for research and learning purposes</div>
    </AbsoluteFill>
  );
};

const PetriNetFormalism: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const places = [
    { id: "p1", x: 100, y: 180, label: "Backlog", tokens: 3, color: "#5c6bc0" },
    { id: "p2", x: 280, y: 180, label: "Ready", tokens: 2, color: "#7986cb" },
    { id: "p3", x: 460, y: 180, label: "In Progress", tokens: 4, color: "#9fa8da" },
    { id: "p4", x: 640, y: 180, label: "Code Review", tokens: 3, color: "#c5cae9" },
    { id: "p5", x: 820, y: 180, label: "QA Testing", tokens: 2, color: "#e8eaf6" },
    { id: "p6", x: 1000, y: 180, label: "Staging", tokens: 1, color: "#3949ab" },
    { id: "p7", x: 1180, y: 180, label: "Production", tokens: 0, color: "#1a237e" },
  ];

  const resources = [
    { id: "r1", x: 460, y: 480, label: "Developers", count: 3, total: 5, color: "#66bb6a" },
    { id: "r2", x: 640, y: 480, label: "Reviewers", count: 2, total: 4, color: "#ffa726" },
    { id: "r3", x: 820, y: 480, label: "QA Engineers", count: 1, total: 3, color: "#ab47bc" },
    { id: "r4", x: 1000, y: 480, label: "Test Env", count: 0, total: 2, color: "#ef5350" },
  ];

  const tickets = [
    { id: "T-101", x: 440, y: 245, state: "active" },
    { id: "T-102", x: 480, y: 245, state: "active" },
    { id: "T-103", x: 620, y: 245, state: "blocked" },
    { id: "T-104", x: 660, y: 245, state: "blocked" },
    { id: "T-105", x: 800, y: 245, state: "active" },
    { id: "T-106", x: 980, y: 245, state: "waiting" },
  ];

  const transitions = places.slice(0, -1).map((_, index) => ({ x: (places[index].x + places[index + 1].x) / 2, y: 180, id: `t${index + 1}` }));

  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0a1628 0%, #1a2744 100%)", padding: 15 }}>
      <h2 style={{ fontSize: 28, color: "#e8e8e8", textAlign: "center", marginBottom: 10, fontWeight: 400 }}>Extended Petri Net: Multi-Branch Workflow with Resource Constraints</h2>
      <svg width={width} height={height - 100} style={{ marginTop: 5 }}>
        {places.slice(0, -1).map((place, index) => {
          const transX = transitions[index].x;
          return (<g key={`arrow-group-${index}`}><line x1={place.x + 38} y1="180" x2={transX - 16} y2="180" stroke="#4fc3f7" strokeWidth="1.5" opacity="0.7" /><line x1={transX + 16} y1="180" x2={places[index + 1].x - 38} y2="180" stroke="#4fc3f7" strokeWidth="1.5" markerEnd="url(#arrowhead)" /></g>);
        })}
        {places.map((place, index) => {
          const scale = interpolate(frame - index * 6, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const pulse = interpolate(Math.sin((frame + index * 5) * 0.08), [-1, 1], [0.95, 1.05], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={place.id} style={{ transform: `scale(${scale * pulse})`, transformOrigin: `${place.x}px ${place.y}px` }}>
              <circle cx={place.x} cy={place.y} r="38" fill="rgba(255,255,255,0.02)" stroke={place.color} strokeWidth="2.5" />
              <circle cx={place.x} cy={place.y} r="34" fill="rgba(255,255,255,0.03)" />
              <text x={place.x} y={place.y - 8} textAnchor="middle" fill="#e8e8e8" fontSize="9" fontWeight="400">{place.label}</text>
              {place.tokens > 0 && <text x={place.x} y={place.y + 14} textAnchor="middle" fill={place.color} fontSize="13" fontWeight="bold">{place.tokens}</text>}
            </g>
          );
        })}
        {transitions.map((trans, index) => {
          const transitionScale = interpolate(frame - 20 - index * 8, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const glow = interpolate(Math.sin((frame + index * 3) * 0.1), [-1, 1], [0.3, 0.7], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={trans.id} style={{ transform: `scale(${transitionScale})`, transformOrigin: `${trans.x}px 180px` }}>
              <rect x={trans.x - 14} y={158} width="28" height="44" fill={`rgba(79, 195, 247, ${glow})`} stroke="#4fc3f7" strokeWidth="1.5" rx="3" />
              <text x={trans.x} y={183} textAnchor="middle" fill="#0a1628" fontSize="8" fontWeight="600">{trans.id}</text>
            </g>
          );
        })}
        {tickets.map((ticket, index) => {
          const appearFrame = index * 10;
          const opacity = interpolate(frame - appearFrame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const floatY = interpolate(Math.sin((frame + index * 10) * 0.05), [-1, 1], [-3, 3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const fillColor = ticket.state === "blocked" ? "#ef5350" : ticket.state === "waiting" ? "#ffa726" : "#66bb6a";
          return (
            <g key={ticket.id} style={{ opacity, transform: `translateY(${floatY}px)` }}>
              <rect x={ticket.x - 28} y={ticket.y - 10} width="56" height="20" fill="#263238" stroke={fillColor} strokeWidth="1.5" rx="4" />
              <text x={ticket.x} y={ticket.y + 4} textAnchor="middle" fill="#b0bec5" fontSize="8.5" fontFamily="monospace">{ticket.id}</text>
              {ticket.state === "blocked" && <text x={ticket.x + 20} y={ticket.y - 8} fill="#ef5350" fontSize="12">⚠️</text>}
            </g>
          );
        })}
        {resources.map((resource, index) => {
          const scale = interpolate(frame - 40 - index * 10, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const resourceColor = resource.count === 0 ? "#ef5350" : resource.count < resource.total / 2 ? "#ffa726" : resource.color;
          return (
            <g key={resource.id} style={{ transform: `scale(${scale})`, transformOrigin: `${resource.x}px ${resource.y}px` }}>
              <rect x={resource.x - 48} y={resource.y - 18} width="96" height="36" fill="rgba(255,255,255,0.03)" stroke={resourceColor} strokeWidth="1.5" rx="6" />
              <text x={resource.x} y={resource.y - 3} textAnchor="middle" fill={resourceColor} fontSize="9" fontWeight="500">{resource.label}</text>
              <text x={resource.x} y={resource.y + 10} textAnchor="middle" fill="#90a4ae" fontSize="8">{resource.count}/{resource.total}</text>
            </g>
          );
        })}
        <line x1="460" y1="225" x2="460" y2="455" stroke="#66bb6a" strokeWidth="1" strokeDasharray="3,3" opacity="0.4" />
        <line x1="640" y1="225" x2="640" y2="455" stroke="#ffa726" strokeWidth="1" strokeDasharray="3,3" opacity="0.4" />
        <line x1="820" y1="225" x2="820" y2="455" stroke="#ab47bc" strokeWidth="1" strokeDasharray="3,3" opacity="0.4" />
        <line x1="1000" y1="225" x2="1000" y2="455" stroke="#ef5350" strokeWidth="1" strokeDasharray="3,3" opacity="0.4" />
        <defs>
          <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#4fc3f7" /></marker>
        </defs>
        {frame > 80 && (
          <g>
            <rect x="120" y="530" width="940" height="55" fill="rgba(239, 83, 80, 0.1)" rx="6" stroke="#ef5350" strokeWidth="1" />
            <text x="580" y="552" textAnchor="middle" fill="#ef5350" fontSize="11" fontWeight="500">⚠️ Deadlock Detected: T-103 and T-104 blocked at Code Review (reviewer contention)</text>
            <text x="580" y="570" textAnchor="middle" fill="#ff7043" fontSize="9">Shared reviewer pool exhausted (2/4) • QA Testing environment unavailable (0/2)</text>
          </g>
        )}
      </svg>
      <div style={{ textAlign: "center", marginTop: 10, fontSize: 10, color: "#546e7a" }}>Educational demonstration • Apache 2.0 License • Non-commercial research use</div>
    </AbsoluteFill>
  );
};

const AnalysisProperties: React.FC = () => {
  const frame = useCurrentFrame();
  const properties = [
    { icon: "⚠️", name: "Deadlock Freedom", desc: "System can always make progress; no circular wait conditions", formal: "∀s ∈ S: ∃t enabled(s)", color: "#ef5350" },
    { icon: "🔗", name: "Boundedness", desc: "Token count in each place remains finite", formal: "∃k: ∀s, ∀p: #tokens(p) ≤ k", color: "#5c6bc0" },
    { icon: "⚡", name: "Liveness", desc: "Every transition can eventually fire", formal: "∀t ∈ T: ◇enabled(t)", color: "#66bb6a" },
    { icon: "🔄", name: "Reversibility", desc: "System can return to initial state", formal: "∀s: s₀ ∈ reachable(s)", color: "#ffa726" },
    { icon: "🎯", name: "Siphon Analysis", desc: "Identifies structural bottlenecks", formal: "S′ ⊆ S: •S′ ⊆ S′•", color: "#ab47bc" },
    { icon: "🌐", name: "Shared State", desc: "Global resource pools couple workflows", formal: "R: ∀w ∈ W: depends(w, r)", color: "#26c6da" },
  ];
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%)", padding: 35 }}>
      <h2 style={{ fontSize: 34, color: "#e8e8e8", textAlign: "center", marginBottom: 28, fontWeight: 400 }}>Formal Properties Analyzed</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, maxWidth: 1000, margin: "0 auto" }}>
        {properties.map((prop, index) => {
          const opacity = interpolate(frame - index * 9, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const slideUp = interpolate(frame - index * 9, [0, 18], [25, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={index} style={{ background: `${prop.color}08`, border: `1px solid ${prop.color}30`, borderRadius: 6, padding: "16px 18px", opacity, transform: `translateY(${slideUp}px)` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}><span style={{ fontSize: 24 }}>{prop.icon}</span><span style={{ fontSize: 16, color: prop.color, fontWeight: 500 }}>{prop.name}</span></div>
              <div style={{ fontSize: 12, color: "#b0bec5", marginBottom: 8, lineHeight: 1.5 }}>{prop.desc}</div>
              <div style={{ fontSize: 11, color: "#78909c", background: "rgba(0,0,0,0.25)", padding: "6px 10px", borderRadius: 4, fontFamily: "monospace", borderLeft: `2px solid ${prop.color}` }}>{prop.formal}</div>
            </div>
          );
        })}
      </div>
      <div style={{ textAlign: "center", marginTop: 22, fontSize: 11, color: "#546e7a" }}>Non-commercial educational project • Apache 2.0 License</div>
    </AbsoluteFill>
  );
};

const ExampleAnalysis: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0a1628 0%, #1a2744 100%)", padding: 32 }}>
      <h2 style={{ fontSize: 30, color: "#e8e8e8", textAlign: "center", marginBottom: 18, fontWeight: 400 }}>Example: Workflow Analysis Output</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, maxWidth: 1020, margin: "0 auto" }}>
        <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 6, padding: 16, border: "1px solid #37474f" }}>
          <h3 style={{ fontSize: 16, color: "#64b5f6", marginBottom: 10, borderBottom: "1px solid #37474f", paddingBottom: 6 }}>Input: Ticket Data</h3>
          {[{ id: "T-101", state: "In Progress", owner: "Alice", blocks: "T-103" }, { id: "T-102", state: "In Progress", owner: "Bob", blocks: "T-105" }, { id: "T-103", state: "Code Review", owner: "Charlie", blocks: "T-104" }, { id: "T-104", state: "Code Review", owner: "Charlie", blocks: "" }, { id: "T-105", state: "QA Testing", owner: "Diana", blocks: "" }].map((ticket, index) => {
            const opacity = interpolate(frame - 8 - index * 5, [0, 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={ticket.id} style={{ background: "rgba(100, 181, 246, 0.06)", border: "1px solid #64b5f630", borderRadius: 4, padding: "7px 10px", marginBottom: 5, opacity, fontSize: 11 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 3 }}><span style={{ fontWeight: 500, color: "#90caf9", fontFamily: "monospace" }}>{ticket.id}</span><span style={{ fontSize: 9, padding: "1.5px 5px", background: "#64b5f620", color: "#64b5f6", borderRadius: 3 }}>{ticket.state}</span></div>
                <div style={{ color: "#b0bec5", fontSize: 10 }}><span>Owner: {ticket.owner}</span>{ticket.blocks && <span style={{ marginLeft: 8, color: "#ef5350" }}>→ blocks {ticket.blocks}</span>}</div>
              </div>
            );
          })}
        </div>
        <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 6, padding: 16, border: "1px solid #37474f" }}>
          <h3 style={{ fontSize: 16, color: "#ef5350", marginBottom: 10, borderBottom: "1px solid #37474f", paddingBottom: 6 }}>Analysis Results</h3>
          {[{ level: "CRITICAL", issue: "Deadlock detected", detail: "T-103 → T-104 blocked (reviewer contention)", color: "#ef5350" }, { level: "WARNING", issue: "Resource exhaustion", detail: "Reviewer pool: 2/4 available", color: "#ff7043" }, { level: "WARNING", issue: "WIP limit exceeded", detail: "Code Review: 47 tokens (limit: 10)", color: "#ffa726" }, { level: "INFO", issue: "Boundedness verified", detail: "All places bounded ✓", color: "#66bb6a" }, { level: "INFO", issue: "Liveness violation", detail: "Transition t₄ not live", color: "#26c6da" }].map((result, index) => {
            const opacity = interpolate(frame - 18 - index * 5, [0, 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={index} style={{ background: `${result.color}08`, border: `1px solid ${result.color}30`, borderRadius: 4, padding: "7px 10", marginBottom: 5, opacity }}>
                <div style={{ fontWeight: 500, color: result.color, fontSize: 11, marginBottom: 2 }}>[{result.level}] {result.issue}</div>
                <div style={{ fontSize: 10, color: "#b0bec5", marginLeft: 2 }}>{result.detail}</div>
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ textAlign: "center", marginTop: 16, fontSize: 10, color: "#546e7a" }}>Educational research tool • Apache 2.0 License • Non-commercial use only</div>
    </AbsoluteFill>
  );
};

const MethodologySlide: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%)", padding: 48 }}>
      <h2 style={{ fontSize: 36, color: "#e8e8e8", textAlign: "center", marginBottom: 32, fontWeight: 400 }}>Methodology</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 820, margin: "0 auto" }}>
        {[{ step: "1", title: "Data Acquisition", desc: "Extract ticket states, transitions, and dependencies via API", detail: "Formal mapping: Tickets → Tokens, States → Places, Actions → Transitions", color: "#5c6bc0" }, { step: "2", title: "Model Construction", desc: "Build Petri net representation with resource pools", detail: "Extended Petri net: ⟨P, T, F, W, R⟩ where R = shared resources", color: "#7986cb" }, { step: "3", title: "Formal Analysis", desc: "Compute reachability graph and verify properties", detail: "State space exploration with max_states bound for tractability", color: "#9fa8da" }, { step: "4", title: "Insight Generation", desc: "Translate formal results to actionable findings", detail: "Severity-ranked: CRITICAL → WARNING → INFO", color: "#c5cae9" }].map((item, index) => {
          const opacity = interpolate(frame - index * 12, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const slideIn = interpolate(frame - index * 12, [0, 15], [-40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={index} style={{ display: "flex", alignItems: "center", gap: 16, background: "rgba(255,255,255,0.03)", borderRadius: 6, padding: "16px 20px", opacity, transform: `translateX(${slideIn}px)`, border: `1px solid ${item.color}20` }}>
              <div style={{ width: 40, height: 40, borderRadius: "50%", background: item.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 600, color: "#0a1628", flexShrink: 0 }}>{item.step}</div>
              <div style={{ flex: 1 }}><div style={{ fontSize: 19, color: item.color, fontWeight: 500, marginBottom: 3 }}>{item.title}</div><div style={{ fontSize: 13, color: "#b0bec5", marginBottom: 3 }}>{item.desc}</div><div style={{ fontSize: 11, color: "#78909c", fontFamily: "monospace", borderLeft: `2px solid ${item.color}`, paddingLeft: 8 }}>{item.detail}</div></div>
            </div>
          );
        })}
      </div>
      <div style={{ textAlign: "center", marginTop: 20, fontSize: 11, color: "#546e7a" }}>Open-source educational project • Apache 2.0 License</div>
    </AbsoluteFill>
  );
};

const ConclusionSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame - 25, [0, 15], [0.92, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #0a1628 0%, #1a2744 100%)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{ transform: `scale(${scale})`, textAlign: "center" }}>
        <h1 style={{ fontSize: 46, color: "#e8e8e8", margin: 0, marginBottom: 20, fontWeight: 300, letterSpacing: "1px" }}>Formal Methods for Workflow Analysis</h1>
        <p style={{ fontSize: 19, color: "#b0bec5", margin: "16px 0 16px 0", maxWidth: 720, lineHeight: 1.6, fontWeight: 300 }}>Applying Petri net theory to identify systemic issues in ticket-based workflows</p>
        <div style={{ marginTop: 28, padding: "14px 28px", background: "rgba(100, 181, 246, 0.12)", borderRadius: 5, border: "1px solid #64b5f640" }}><code style={{ fontSize: 16, color: "#64b5f6", fontFamily: "monospace" }}>petri-workflow-analysis</code></div>
        <div style={{ marginTop: 22, fontSize: 11, color: "#546e7a" }}>Educational Research Project • Apache 2.0 License • Non-Commercial Use</div>
        <div style={{ marginTop: 8, fontSize: 10, color: "#455a64" }}>Created for academic and research purposes</div>
      </div>
    </AbsoluteFill>
  );
};

export const JiraPetriSkillExplainer: React.FC = () => {
  const fps = 30;
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={fps * 4}><TitleSlide /></Sequence>
      <Sequence from={fps * 4} durationInFrames={fps * 5}><MotivationSlide /></Sequence>
      <Sequence from={fps * 9} durationInFrames={fps * 7}><PetriNetFormalism /></Sequence>
      <Sequence from={fps * 16} durationInFrames={fps * 7}><AnalysisProperties /></Sequence>
      <Sequence from={fps * 23} durationInFrames={fps * 6}><ExampleAnalysis /></Sequence>
      <Sequence from={fps * 29} durationInFrames={fps * 6}><MethodologySlide /></Sequence>
      <Sequence from={fps * 35} durationInFrames={fps * 5}><ConclusionSlide /></Sequence>
    </AbsoluteFill>
  );
};
