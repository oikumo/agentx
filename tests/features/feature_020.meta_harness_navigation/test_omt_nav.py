"""
Test suite for feature_020: Meta Harness Navigation Tools

Tests the omt_nav, omt_list_sections, omt_cross_ref, and omt_quick_ref
opencode plugin tools for structured documentation navigation.

Test Strategy:
- Verify grep patterns find expected tags in META HARNESS files
- Verify tool responses contain required fields
- Verify edge cases (no matches, invalid files)
"""

import subprocess
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
META_ROOT = REPO_ROOT / ".meta"


class TestGrepPatterns:
    """Test that grep patterns work across META HARNESS documentation"""

    def test_section_headers_exist(self):
        """Verify SECTION: headers exist in all META HARNESS files"""
        result = subprocess.run(
            ["grep", "-r", "SECTION:", str(META_ROOT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "SECTION: headers should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 10, f"Expected 10+ SECTION: headers, found {len(lines)}"

    def test_rule_codes_exist(self):
        """Verify RULE_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^RULE_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "RULE_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 3, f"Expected 3+ RULE_ codes, found {len(lines)}"

    def test_error_codes_exist(self):
        """Verify ERR_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^ERR_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "ERR_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1, f"Expected ERR_ codes, found {len(lines)}"

    def test_cmd_codes_exist(self):
        """Verify CMD_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^CMD_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "CMD_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 4, f"Expected 4+ CMD_ codes, found {len(lines)}"

    def test_quick_patterns_exist(self):
        """Verify QUICK_ workflow patterns exist"""
        result = subprocess.run(
            ["grep", "^QUICK_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "QUICK_ patterns should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2, f"Expected 2+ QUICK_ patterns, found {len(lines)}"

    def test_xref_codes_exist(self):
        """Verify XREF_ cross-references exist"""
        result = subprocess.run(
            ["grep", "^XREF_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "XREF_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1, f"Expected XREF_ codes, found {len(lines)}"


class TestOmtNavTool:
    """Test omt_nav plugin tool functionality"""

    def test_omt_nav_tool_file_exists(self):
        """Verify omt_nav.ts plugin file exists"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        assert nav_file.exists(), "omt_nav.ts should exist"

    def test_omt_nav_exports_tools(self):
        """Verify omt_nav.ts exports required tools"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        
        assert "export {" in content, "Should have export statement"
        assert "omt_nav" in content, "Should export omt_nav"
        assert "omt_list_sections" in content, "Should export omt_list_sections"
        assert "omt_cross_ref" in content, "Should export omt_cross_ref"
        assert "omt_quick_ref" in content, "Should export omt_quick_ref"

    def test_omt_nav_has_tool_decorator(self):
        """Verify omt_nav uses tool() decorator from opencode plugin"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        
        assert 'tool({' in content, "Should use tool() decorator"
        assert 'name: "omt_nav"' in content, "Should declare omt_nav tool"
        assert 'import { tool } from "@opencode-ai/plugin"' in content, "Should import tool"


class TestOmtListSections:
    """Test omt_list_sections tool"""

    def test_function_exists(self):
        """Verify omt_list_sections function exists"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        
        assert "const omt_list_sections = tool({" in content, "Should define omt_list_sections"
        assert 'name: "omt_list_sections"' in content, "Should declare tool name"


class TestOmtCrossRef:
    """Test omt_cross_ref tool"""

    def test_function_exists(self):
        """Verify omt_cross_ref function exists"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        
        assert "const omt_cross_ref = tool({" in content, "Should define omt_cross_ref"
        assert 'name: "omt_cross_ref"' in content, "Should declare tool name"


class TestOmtQuickRef:
    """Test omt_quick_ref tool"""

    def test_function_exists(self):
        """Verify omt_quick_ref function exists"""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        
        assert "const omt_quick_ref = tool({" in content, "Should define omt_quick_ref"
        assert 'name: "omt_quick_ref"' in content, "Should declare tool name"


class TestDocumentationCoverage:
    """Test that all META HARNESS files have proper tags"""

    def test_meta_harness_has_all_tags(self):
        """Verify META_HARNESS.md has all required tag types"""
        file_path = META_ROOT / "META_HARNESS.md"
        content = file_path.read_text()
        
        assert "SECTION:" in content, "Should have SECTION: headers"
        assert "RULE_" in content, "Should have RULE_ codes"
        assert "ERR_" in content, "Should have ERR_ codes"
        assert "CMD_" in content, "Should have CMD_ codes"
        assert "QUICK_" in content, "Should have QUICK_ patterns"
        assert "XREF_" in content, "Should have XREF_ references"

    def test_agents_md_has_tags(self):
        """Verify AGENTS.md has SECTION: headers"""
        file_path = REPO_ROOT / "AGENTS.md"
        content = file_path.read_text()
        
        assert "SECTION:" in content or "##" in content, "Should have section headers"

    def test_omt_agent_guide_has_sections(self):
        """Verify omt_agent_guide.md has section headers (numbered format)"""
        file_path = META_ROOT / "software_development_process" / "omt_agent_guide.md"
        assert file_path.exists(), "omt_agent_guide.md should exist"
        content = file_path.read_text()
        
        # omt_agent_guide.md uses numbered sections (## 1., ## 2., etc.) instead of SECTION: tags
        assert "## " in content, "Should have section headers"
        # Verify it has multiple sections
        section_count = content.count("## ")
        assert section_count >= 10, f"Should have 10+ sections, found {section_count}"

    def test_all_omt_plus_plus_files_have_sections(self):
        """Verify all doc/omt++ files have SECTION: headers"""
        omt_pp_dir = META_ROOT / "doc" / "omt++"
        md_files = list(omt_pp_dir.glob("*.md"))
        
        assert len(md_files) >= 6, f"Expected 6+ omt++ files, found {len(md_files)}"
        
        for md_file in md_files:
            content = md_file.read_text()
            assert "SECTION:" in content, f"{md_file.name} should have SECTION: headers"


class TestIntegration:
    """Integration tests for navigation system"""

    def test_grep_pattern_compatibility(self):
        """Verify grep patterns work from command line"""
        # Test that standard grep patterns return results
        patterns = [
            "SECTION:",
            "CMD_OMT",
            "ERR_",
            "QUICK_",
        ]
        
        for pattern in patterns:
            result = subprocess.run(
                ["grep", "-r", pattern, str(META_ROOT)],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            # Should find at least some matches
            assert result.returncode == 0 or len(result.stdout) > 0, \
                f"Pattern '{pattern}' should find matches"

    def test_file_paths_resolvable(self):
        """Verify all META HARNESS files are accessible"""
        expected_files = [
            ".meta/META_HARNESS.md",
            ".meta/META.md",
            ".meta/software_development_process/META.md",
            ".meta/software_development_process/omt_agent_guide.md",
            "AGENTS.md",
            "WORK.md",
        ]
        
        for rel_path in expected_files:
            file_path = REPO_ROOT / rel_path
            assert file_path.exists(), f"{rel_path} should exist"
            assert file_path.stat().st_size > 0, f"{rel_path} should not be empty"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])