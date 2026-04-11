# Jira Petri Net Analyzer Skill - Explainer Video

This Remotion project creates an animated explainer video for the Jira Petri Net Analyzer skill.

## What It Covers

The video explains:
1. **Title Slide** - Introduction to the Jira Petri Net Analyzer
2. **What It Does** - Key features and capabilities
3. **Petri Net Model** - Visual representation of workflow states and transitions
4. **Analysis Properties** - Formal verification properties (boundedness, liveness, etc.)
5. **How It Works** - Integration workflow with Jira via MCP
6. **Final Slide** - Call to action

## Commands

### Start Development Server
```bash
npm run dev
```

### Render Video
```bash
npx remotion render
```

### Render Single Frame (for preview)
```bash
npx remotion still JiraPetriSkillExplainer --scale=0.25 --frame=30
```

## Composition Details

- **ID**: `JiraPetriSkillExplainer`
- **Duration**: 32 seconds (960 frames @ 30fps)
- **Resolution**: 1280x720
- **FPS**: 30

## Scenes

1. **Title Slide** (0-4s) - Animated title with gradient background
2. **What It Does** (4-9s) - Feature list with spring animations
3. **Petri Net Visualization** (9-15s) - Diagram of workflow states
4. **Analysis Properties** (15-21s) - Grid of verification properties
5. **How It Works** (21-27s) - Step-by-step integration flow
6. **Final Slide** (27-32s) - Conclusion and skill name

## Skills Demonstrated

- ✅ Spring animations for smooth transitions
- ✅ Sequence timing for scene management
- ✅ SVG graphics for Petri net diagram
- ✅ Gradient backgrounds
- ✅ Responsive text sizing
- ✅ Color-coded sections
