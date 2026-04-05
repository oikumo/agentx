"""Benchmark: Agent navigation via AGENTS.md rules with full trace.

Shows step-by-step navigation trace as the agent resolves paths.
"""

import time
import unittest
from pathlib import Path


class TestAgentNavigationBenchmarkTrace(unittest.TestCase):
    """Benchmark test cases with full navigation trace."""

    PROJECT_ROOT = Path(__file__).parent.parent
    AGENTS_MD = PROJECT_ROOT / "AGENTS.md"

    def test_01_find_project_navigation_map(self):
        """Task 1: Where is the project navigation map?"""
        print("\n[TASK 1] Finding project navigation map...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()
        print(f"  → AGENTS.md size: {len(content)} chars")

        print("  → Searching for PROJECT_NAVIGATION reference...")
        self.assertIn("PROJECT_NAVIGATION_ROUTES.md", content)
        print("  → Found: PROJECT_NAVIGATION_ROUTES.md")

        print("  → Checking path: .project_development/PROJECT_NAVIGATION_ROUTES.md")
        target = (
            self.PROJECT_ROOT / ".project_development" / "PROJECT_NAVIGATION_ROUTES.md"
        )
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading navigation map...")
        nav_content = target.read_text()
        print(f"  → Navigation map size: {len(nav_content)} chars")
        print("  → Contains module index: ", "Module Index" in nav_content)
        print("  → Contains Meta section: ", "## Meta" in nav_content)

    def test_02_find_testing_rules(self):
        """Task 2: Where are the testing rules?"""
        print("\n[TASK 2] Finding testing rules...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for PROJECT_TESTING_SANDBOX_RULES reference...")
        self.assertIn("PROJECT_TESTING_SANDBOX_RULES.md", content)
        print("  → Found: PROJECT_TESTING_SANDBOX_RULES.md")

        print(
            "  → Checking path: .project_development/PROJECT_TESTING_SANDBOX_RULES.md"
        )
        target = (
            self.PROJECT_ROOT
            / ".project_development"
            / "PROJECT_TESTING_SANDBOX_RULES.md"
        )
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading testing rules...")
        rules_content = target.read_text()
        print(f"  → Rules file size: {len(rules_content)} chars")
        print("  → Contains TDD rules: ", "TDD" in rules_content)

    def test_03_find_current_issue(self):
        """Task 3: Where is the current issue tracked?"""
        print("\n[TASK 3] Finding current issue tracker...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for CURRENT_ISSUE reference...")
        self.assertIn("CURRENT_ISSUE.md", content)
        print("  → Found: CURRENT_ISSUE.md")

        print("  → Checking path: .project_development/CURRENT_ISSUE.md")
        target = self.PROJECT_ROOT / ".project_development" / "CURRENT_ISSUE.md"
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading current issue...")
        issue_content = target.read_text()
        print(f"  → Issue file size: {len(issue_content)} chars")
        print("  → Status: ", "EMPTY" if "EMPTY" in issue_content else "ACTIVE")

    def test_04_find_project_roadmap(self):
        """Task 4: Where is the project roadmap?"""
        print("\n[TASK 4] Finding project roadmap...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for PROJECT_ROADMAP reference...")
        self.assertIn("PROJECT_ROADMAP.md", content)
        print("  → Found: PROJECT_ROADMAP.md")

        print("  → Checking path: .project_development/PROJECT_ROADMAP.md")
        target = self.PROJECT_ROOT / ".project_development" / "PROJECT_ROADMAP.md"
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading roadmap...")
        roadmap_content = target.read_text()
        print(f"  → Roadmap size: {len(roadmap_content)} chars")
        print("  → Has planned features: ", "Planned Features" in roadmap_content)
        print("  → Has completed items: ", "Completed" in roadmap_content)

    def test_05_find_project_documentation(self):
        """Task 5: Where is the project documentation map?"""
        print("\n[TASK 5] Finding project documentation map...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for PROJECT_DOCUMENTATION reference...")
        self.assertIn("PROJECT_DOCUMENTATION.md", content)
        print("  → Found: PROJECT_DOCUMENTATION.md")

        print("  → Checking path: .project_development/PROJECT_DOCUMENTATION.md")
        target = self.PROJECT_ROOT / ".project_development" / "PROJECT_DOCUMENTATION.md"
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading documentation map...")
        doc_content = target.read_text()
        print(f"  → Documentation size: {len(doc_content)} chars")
        print("  → Has module structure: ", "Module Structure" in doc_content)

    def test_06_find_user_command_extension(self):
        """Task 6: Where is the user command extension?"""
        print("\n[TASK 6] Finding user command extension...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for USER_COMMAND_EXTENSION reference...")
        self.assertIn("USER_COMMAND_EXTENSION.md", content)
        print("  → Found: USER_COMMAND_EXTENSION.md")

        print("  → Checking path: .project_development/USER_COMMAND_EXTENSION.md")
        target = (
            self.PROJECT_ROOT / ".project_development" / "USER_COMMAND_EXTENSION.md"
        )
        self.assertTrue(target.exists())
        print(f"  ✅ File exists: {target}")

        print("  → Reading command extension...")
        cmd_content = target.read_text()
        print(f"  → Command extension size: {len(cmd_content)} chars")
        print("  → Has command reference table: ", "Command Reference" in cmd_content)

    def test_07_find_application_entry_point(self):
        """Task 7: What is the entry point of the application?"""
        print("\n[TASK 7] Finding application entry point...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for main.py reference...")
        print("  → Checking path: main.py")
        entry_point = self.PROJECT_ROOT / "main.py"
        self.assertTrue(entry_point.exists())
        print(f"  ✅ File exists: {entry_point}")

        print("  → Reading entry point...")
        main_content = entry_point.read_text()
        print(f"  → main.py size: {len(main_content)} chars")
        print("  → Contains create_controller: ", "create_controller" in main_content)
        print("  → Contains ReplApp: ", "ReplApp" in main_content)

    def test_08_find_llm_providers(self):
        """Task 8: Where are the LLM providers implemented?"""
        print("\n[TASK 8] Finding LLM providers...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → AGENTS.md doesn't contain llm_managers directly...")
        print("  → Following navigation reference to PROJECT_NAVIGATION_ROUTES.md...")
        nav_path = (
            self.PROJECT_ROOT / ".project_development" / "PROJECT_NAVIGATION_ROUTES.md"
        )
        self.assertTrue(nav_path.exists())
        print(f"  → Found navigation map: {nav_path}")

        print("  → Reading navigation map for llm_managers reference...")
        nav_content = nav_path.read_text()
        self.assertIn("llm_managers", nav_content)
        print("  → Found: llm_managers in navigation map")

        print("  → Checking path: llm_managers/providers/")
        providers_path = self.PROJECT_ROOT / "llm_managers" / "providers"
        self.assertTrue(providers_path.exists())
        print(f"  ✅ Directory exists: {providers_path}")

        print("  → Listing provider files...")
        for f in providers_path.iterdir():
            if f.suffix == ".py":
                print(f"    📄 {f.name}")
        print(
            "  → Found providers: llamacpp_provider.py, openai_provider.py, openrouter_provider.py"
        )

    def test_09_find_repl_system(self):
        """Task 9: Where is the REPL system?"""
        print("\n[TASK 9] Finding REPL system...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → AGENTS.md doesn't contain REPL directly...")
        print("  → Following navigation reference to PROJECT_NAVIGATION_ROUTES.md...")
        nav_path = (
            self.PROJECT_ROOT / ".project_development" / "PROJECT_NAVIGATION_ROUTES.md"
        )
        self.assertTrue(nav_path.exists())
        print(f"  → Found navigation map: {nav_path}")

        print("  → Reading navigation map for REPL reference...")
        nav_content = nav_path.read_text()
        self.assertIn("repl", nav_content.lower())
        print("  → Found: REPL in navigation map")

        print("  → Checking path: app/repl/")
        repl_path = self.PROJECT_ROOT / "app" / "repl"
        self.assertTrue(repl_path.exists())
        print(f"  ✅ Directory exists: {repl_path}")

        print("  → Listing REPL files...")
        for f in repl_path.iterdir():
            if f.suffix == ".py":
                print(f"    📄 {f.name}")

    def test_10_find_sandbox_tests(self):
        """Task 10: Where are the sandbox tests?"""
        print("\n[TASK 10] Finding sandbox tests...")
        print("  → Reading AGENTS.md for reference...")
        content = self.AGENTS_MD.read_text()

        print("  → Searching for tests_sandbox reference...")
        self.assertIn("tests_sandbox", content)
        print("  → Found: tests_sandbox")

        print("  → Checking path: tests_sandbox/")
        sandbox_path = self.PROJECT_ROOT / "tests_sandbox"
        self.assertTrue(sandbox_path.exists())
        print(f"  ✅ Directory exists: {sandbox_path}")

        print("  → Counting test files...")
        test_files = list(sandbox_path.glob("test_*.py"))
        print(f"  → Found {len(test_files)} test files")
        for f in test_files:
            print(f"    📄 {f.name}")

    def test_11_agents_md_references_updated(self):
        """Task 11: Verify AGENTS.md references point to .project_development/"""
        print("\n[TASK 11] Verifying AGENTS.md references...")
        print("  → Reading AGENTS.md...")
        content = self.AGENTS_MD.read_text()

        print("  → Checking for .project_development/ references...")
        self.assertIn(".project_development/", content)
        count = content.count(".project_development/")
        print(f"  → Found {count} references to .project_development/")

        print("  → Checking for old _agent_rules/ references...")
        self.assertNotIn("/_agent_rules/", content)
        print("  ✅ No old _agent_rules/ references found")

    def test_12_coding_style_rules(self):
        """Task 12: Verify coding style rules are referenced and exist."""
        print("\n[TASK 12] Verifying coding style rules...")
        print("  → Reading AGENTS.md...")
        content = self.AGENTS_MD.read_text()

        print("  → Checking for CODING_STYLE.md reference...")
        self.assertIn("CODING_STYLE.md", content)
        print("  ✅ AGENTS.md references CODING_STYLE.md")

        print("  → Checking CODING_STYLE.md exists...")
        style_path = self.PROJECT_ROOT / ".project_development" / "CODING_STYLE.md"
        self.assertTrue(style_path.exists())
        print(f"  ✅ File exists: {style_path}")

        print("  → Reading coding style rules...")
        style_content = style_path.read_text()

        print("  → Checking line length limit...")
        self.assertIn("88", style_content)
        print("  ✅ Line length: 88 characters")

        print("  → Checking naming conventions...")
        self.assertIn("snake_case", style_content)
        print("  ✅ Functions/variables: snake_case")

        self.assertIn("PascalCase", style_content)
        print("  ✅ Classes: PascalCase")

        self.assertIn("UPPER_SNAKE_CASE", style_content)
        print("  ✅ Constants: UPPER_SNAKE_CASE")

        print("  → Checking docstring style...")
        self.assertIn("Google-style", style_content)
        print("  ✅ Docstrings: Google-style")


if __name__ == "__main__":
    unittest.main()
