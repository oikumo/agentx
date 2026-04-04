AGENTS.md - Agent-X RULES
-------------------------

System Agent coding entry point. ALWAYS FOLLOW THIS RULES

[# Rules]()

[RULES]
<INSTRUCTIONS>: In [## System Instructions]().
<USER_COMMANDS>: In [## Opencode editor User Commands]().
<USER_COMMAND_EXTENSION>: In [## User Commands Extension]()
<PROJECT_NAVIGATION>: In [## Project Navigation]().
<PROJECT_DOCUMENTATION>: In [## Project Documentation]().
<PROJECT_TESTING_SANDBOX_RULES>: In [## Project Testing Sandbox Rules]().
<PROJECT_ROADMAP>: In [## Project Roadmap]().
<TAKS_TYPES>: In [## Tasks Types]().
<CURRENT_ISSUE>: In [## Current Issue](). 
<GENERAL_RULES>: In [## General Rules]().
[/RULES]

[## System Instructions]()

<INSTRUCTIONS>
<INSTRUCTION>NEVER ADD A NEW DEPENDENCIES, JUST USE THE EXISTING ONES</INSTRUCTION>
<INSTRUCTION>NEVER SEE, INSPECT, COPY, STORE OR CHANGE .env FILE</INSTRUCTION>
<INSTRUCTION>BEFORE ANY ACTION CHECK THE LAST COMMIT IN GIT</INSTRUCTION>
<INSTRUCTION>Never commit files that likely contain secrets (.env, credentials.json, etc.)</INSTRUCTION>
<INSTRUCTION>NEVER EXECUTE git commit and push commands, DESPITE THE USER ASK FOR IT. NEVER DO IT THE USER CAN'T APPROVE THIS COMMANDS</INSTRUCTION>
<INSTRUCTION>Tests folder tests/ NEVER CAN BE CHANGE BY THE SYSTEM</INSTRUCTION>
<INSTRUCTION>Tests folder tests_sandbox/ can be used BY THE SYSTEM, but REQUIRES EXPLICIT USER APPROVAL. The test use unittest.TestCase class framework</INSTRUCTION>
<INSTRUCTION>Tests folder tests_sandbox/ implementation must follow </INSTRUCTION>
<INSTRUCTION>Environment variables should live in .env and not be committed</INSTRUCTION>
<INSTRUCTION>Dependency management via pyproject.toml and uv tooling; avoid pin drift</INSTRUCTION>
</INSTRUCTIONS>

[## Opencode editor User Commands]()

Commands names allways starts with the prefix: "+".

* Commands list:

[<USER_COMMANDS>]()

<USER_COMMAND>
  <NAME>+reload</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>Check the last 10 commits and read again the file "AGENTS.md"</ACTION>
</USER_COMMAND>


<USER_COMMAND>
  <NAME>+fix</NAME>
  <ARGUMENTS>{bug information}</ARGUMENTS>
  <ACTION>Fix the bug introduced by last changes, based on {bug information} User argument. Check the last 10 commits and the ones that are in staging</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+issue</NAME>
  <ARGUMENTS>{current_issue_description}</ARGUMENTS>
  <ACTION>Update or set the [## Current Issue]() described by the User in the argument: {current_issue_description}. If the issue is solved, APPLY THE RULES IN [## Current Issue]()</ACTION>
</USER_COMMAND>


<USER_COMMAND>
  <NAME>+solve</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>Solve the [## Current Issue](), is a BIG TASK [<NAME>BIG TASK<NAME>](). If the issue is solved, APPLY THE RULES IN [## Current Issue]()</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+?</NAME>
  <ARGUMENTS>{question_about_the_project}</ARGUMENTS>
  <ACTION>Question about the project, allways check the last 50 commits</ACTION>
</USER_COMMAND>

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+find</NAME>
  <ARGUMENTS>{module or topic}</ARGUMENTS>
  <ACTION>Find what the User say in the argument {module or topic}. Before anything use as reference [## Project Navigation]() </ACTION>
</USER_COMMAND>

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+update</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>Update [## Project Navigation](), [## Current Issue]() and [## Project Documentation]() and derived files according the changes in the last 50 commits. assume it is a BIG TASK [<NAME>BIG TASK<NAME>]()</ACTION>
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

<USER_COMMANDS>
<USER_COMMAND>
  <NAME>+</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>List all User Commands in [<USER_COMMANDS>]() and [## User Commands Extension]() (file: "/USER_COMMAND_EXTENSION.md"), include a description. Format it in a simple .MD table</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+test</NAME>
  <ARGUMENTS></ARGUMENTS>
  <ACTION>System run tests in folder "/tests_sandbox" only</ACTION>
</USER_COMMAND>

<USER_COMMAND>
  <NAME>+tdd</NAME>
  <ARGUMENTS>{implementation_test_scope}</ARGUMENTS>
  <ACTION>System apply TDD given the scope in the User argument {implementation_test_scope} in folder "/tests_sandbox" only, following the RULES</ACTION>
</USER_COMMAND>

</USER_COMMANDS>

[## User Commands Extension]()

<USER_COMMAND_EXTENSION>
<DESCRIPTION>
User Command extensión in file "/USER_COMMAND_EXTENSION.md"
</DESCRIPTION>
</USER_COMMAND_EXTENSION>


[## Project Testing Sandbox Rules]()

<PROJECT_TESTING_SANDBOX_RULES>
<DESCRIPTION>
Establish the rules to follow implement tests 
</DESCRIPTION>
<ACTION>
Use for know how to implement test following the rules in "/PROJECT_TESTING_SANDBOX_RULES.md" file
</ACTION>
</PROJECT_TESTING_SANDBOX_RULES>

[## Project Navigation]()

<PROJECT_NAVIGATION>
<DESCRIPTION>
MAP TO UNDERSTAND AND NAVIGATE QUICKLY THROUGH THE SOURCE CODE IS IN "/PROJECT_NAVIGATION_ROUTES.md" file
</DESCRIPTION>
<ACTION>
Inspect and make changes but first look in the /PROJECT_NAVIGATION_ROUTES.md file
</ACTION>
</PROJECT_NAVIGATION>

[## Project Documentation]()

<PROJECT_DOCUMENTATION>
<DESCRIPTION>
Project full documentation. Documentation maps folder content in "/PROJECT_DOCUMENTATION.md" file
</DESCRIPTION>
<ACTION>
Check the documentation "/PROJECT_DOCUMENTATION.md" file to navigate in the project documentation, when you need more detailed information
</ACTION>
<PROJECT_DOCUMENTATION>

[## Project Roadmap]()

<PROJECT_ROADMAP>
<DESCRIPTION>
Project new features and improvements. Centralized in the "/PROJECT_ROADMAP.md" file
</DESCRIPTION>
<ACTION>
Take information from here to implement new features or improvements of the project as a whole
</ACTION>
<PROJECT_ROADMAP>

[## Tasks Types]()

<TASK_TYPES>
<TASK_TYPE>
[<NAME>BIG TASK<NAME>]()
<DESCRIPTION>TASK REQUIRE BIG EFFORT AND TAKE TIME BECAUSE IS IMPORTANT. ANALYZE AND THINK CAREFULLY BEFORE GIVE AN ASWER</DESCRIPTION>
</TASK_TYPE>
</TASK_TYPES>

[## Current Issue]()

<CURRENT_ISSUE>
<DESCRIPTION>
Describe the current issue, active and need to be solved in the "/CURRENT_ISSUE.md" file. If is not exists any issue "/CURRENT_ISSUE.md" file, must be set EMPTY 
</DESCRIPTION>
<ACTION>
Put the current issue and current issue solving strategy in "/CURRENT_ISSUE.md" file. If is not exists any issue "/CURRENT_ISSUE.md" file, must be set EMPTY
</ACTION>
<CURRENT_ISSUE>

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
- Language: Python 3.14+; type hints preferred where beneficial.
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

  

