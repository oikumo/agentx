# FEATURE SUMMARY: feature_001.session_user_objectives_driven_by_Petri_Net

The agentx application must have a internal state with a context, sensors and actuators.

The agentx must store it internal state using a adaptative Petri Net to handle it in a concurrent way.

The internal state must be implemented in a single module, `src/agentx/model/internal_state`

The input where the Petri Net is stored is in `local_sessions/current/USER_OBJECTIVES.md`. The Petri Net structure must be updated if the crc of the file changes.

