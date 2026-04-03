AGENTS.md - Agent-X
-------------------

System Agent coding entry point.

[# Rules]()

[RULES]
<INSTRUCTIONS>: In [## System Instructions]().
<USER_COMMANDS>: In [## Opencode editor User Commands]().
<PROJECT_NAVIGATION>: In [## Project Navigation]().
<TAKS_TYPES>: In [## Tasks Types]().
<GENERAL_RULES>: In [## General Rules]().
[/RULES]

[## System Instructions]()

<INSTRUCTIONS>
<INSTRUCTION>NEVER SEE, INSPECT, COPY, STORE OR CHANGE .env FILE</INSTRUCTION>
<INSTRUCTION>BEFORE ANY ACTION CHECK THE LAST COMMIT IN GIT</INSTRUCTION>
<INSTRUCTION>Never commit files that likely contain secrets (.env, credentials.json, etc.)</INSTRUCTION>
<INSTRUCTION>Git commit and push commands REQUIRES EXPLICIT USER APPROVAL</INSTRUCTION>
<INSTRUCTION>Tests folder tests/ NEVER CAN BE CHANGE BY THE SYSTEM, REQUIRES EXPLICIT USER APPROVAL</INSTRUCTION>
<INSTRUCTION>Environment variables should live in .env and not be committed</INSTRUCTION>
<INSTRUCTION>Dependency management via pyproject.toml and uv tooling; avoid pin drift</INSTRUCTION>
</INSTRUCTIONS>

[## Opencode editor User Commands]()

Commands names allways starts with the prefix: "+".

* Commands list:

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+update</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>Update [## Project Navigation]() and derived files according the changes in the last 10 commits</ACTION>
</USER_COMMAND>

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+list</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>List all [# Rules]() in TABLES in MD FORMAT</ACTION>
</USER_COMMAND>

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+focus</NAME>
  <ARGUMENTS>
    <ARGUMENT>
     <DESCRIPTION>FOCUS ON ONE MODULE OR TOPIC</DESCRIPTION>
    </ARGUMENT>
  </ARGUMENTS>
  <ACTION>Focus your attention on ONE MODULE OR TOPIC, before anything use as reference [## Project Navigation]() </ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+tasks</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>List system task, the current one and the past ones</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+tree</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>List all project routes using as reference [## Project Navigation]()</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+big</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>A new BIG_TASK BEGIN [<NAME>BIG TASK<NAME>]()</ACTION>
</USER_COMMAND>

</USER_COMMANDS>

[## Project Navigation]()

<PROJECT_NAVIGATION>
<DESCRIPTION>
MAP TO UNDERSTAND AND NAVIGATE QUICKLY THROUGH THE SOURCE CODE IS IN "/PROJECT_NAVIGATION_ROUTES.md" file
</DESCRIPTION>
<ACTION>
Inspect and make changes but first look in the /PROJECT_NAVIGATION_ROUTES.md file
</ACTION>
</PROJECT_NAVIGATION>

[## Tasks Types]()

<TASK_TYPES>
<TASK_TYPE>
[<NAME>BIG TASK<NAME>]()
<DESCRIPTION>TASK REQUIRE BIG EFFORT AND TAKE TIME BECAUSE IS IMPORTANT. ANALYZE AND THINK CAREFULLY BEFORE GIVE AN ASWER</DESCRIPTION>
</TASK_TYPE>
</TASK_TYPES>

[## General Rules]()

<GENERAL_RULES>
<TOOLS_USAGE>
<TOOL_USAGE>
<CATEGORY>CODING</CATEGORY>
<DESCRIPTION>
Prefer specialized file operations tools over bash commands:
  - Use Glob for file search (not find or ls)
  - Use Grep for content search (not grep or rg)
  - Use Read for reading files (not cat/head/tail)
  - Use Edit for file modifications (not sed/awk)
  - Use Write for creating new files (only when explicitly required)
- When issuing multiple independent bash commands, batch them in parallel
- Avoid using cd <directory> && <command> patterns; use workdir parameter instead
- Use search tools (Glob, Grep) extensively to understand the codebase before making changes
- Implement solutions using all available tools
- Verify solutions with tests when possible
- When editing files, preserve exact indentation and formatting style
<DESCRIPTION>
</TOOLS_USAGE>
<COMMUNICATION>
- Output text directly to communicate with the user; don't use echo/printf for tool results
- When file search or content search is needed, use the appropriate specialized tools
- If uncertain about file paths, use Glob to look up filenames first
</COMMUNICATION>
<CODING_STYLE_GIDELINES>
<GENERAL>
- Language: Python 3.13+; type hints preferred where beneficial.
- Line length: 88 characters.
- Docstrings: Google-style for public functions/classes.
- Tests: mirror source structure; unit tests focus on pure logic; integration tests cover end-to-end flows.
</GENERAL>
<NAMING_CONVENTIONS>
- Functions/variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private members: _prefix
- Modules/files: snake_case.py
</NAMING_CONVENTIONS>
</CODING_STYLE_GIDELINES>

</GENERAL_RULES>

  

