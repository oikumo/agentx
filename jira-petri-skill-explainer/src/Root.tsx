import "./index.css";
import { Composition } from "remotion";
import { JiraPetriSkillExplainer } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="JiraPetriSkillExplainer"
        component={JiraPetriSkillExplainer}
        durationInFrames={960}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{}}
      />
    </>
  );
};
