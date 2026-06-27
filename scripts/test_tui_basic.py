#!/usr/bin/env python3
"""Test script for TUI infrastructure.

This script tests the basic TUI infrastructure without requiring full integration.
Run with: uv run python scripts/test_tui_basic.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all TUI modules can be imported."""
    print("Testing TUI imports...")
    
    try:
        from agentx.ui.interfaces import IMainView, IRagView, IChatView, IUIProvider
        print("✓ Interfaces imported")
    except Exception as e:
        print(f"✗ Failed to import interfaces: {e}")
        return False
    
    try:
        from agentx.ui.providers import ProviderRegistry, ConsoleProvider
        print("✓ Providers imported")
    except Exception as e:
        print(f"✗ Failed to import providers: {e}")
        return False
    
    try:
        from agentx.ui.tui.provider import TUIProvider
        print("✓ TUI Provider imported")
    except Exception as e:
        print(f"✗ Failed to import TUI provider: {e}")
        return False
    
    try:
        from agentx.ui.tui.app import TUIApplication, MainTUIScreen
        print("✓ TUI App imported")
    except Exception as e:
        print(f"✗ Failed to import TUI app: {e}")
        return False
    
    try:
        from agentx.ui.tui.adapters.main_adapter import TUIAdapter
        print("✓ Main adapter imported")
    except Exception as e:
        print(f"✗ Failed to import main adapter: {e}")
        return False
    
    try:
        from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter
        print("✓ RAG adapter imported")
    except Exception as e:
        print(f"✗ Failed to import RAG adapter: {e}")
        return False
    
    try:
        from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
        print("✓ Chat adapter imported")
    except Exception as e:
        print(f"✗ Failed to import chat adapter: {e}")
        return False
    
    return True


def test_provider_registry():
    """Test provider registry functionality."""
    print("\nTesting provider registry...")
    
    from agentx.ui.providers import ProviderRegistry
    
    try:
        providers = ProviderRegistry.list_providers()
        print(f"✓ Registered providers: {providers}")
        
        if "console" not in providers:
            print("✗ Console provider not registered")
            return False
        
        if "tui" not in providers:
            print("✗ TUI provider not registered")
            return False
        
        console = ProviderRegistry.get("console")
        print(f"✓ Got console provider: {type(console).__name__}")
        
        tui = ProviderRegistry.get("tui")
        print(f"✓ Got TUI provider: {type(tui).__name__}")
        
        default = ProviderRegistry.get_default()
        print(f"✓ Got default provider: {type(default).__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Provider registry test failed: {e}")
        return False


def test_interface_abc():
    """Test that interfaces are proper ABCs."""
    print("\nTesting interface ABCs...")
    
    from abc import ABC
    from agentx.ui.interfaces import IMainView, IRagView, IChatView, IUIProvider
    
    try:
        assert issubclass(IMainView, ABC), "IMainView is not an ABC"
        print("✓ IMainView is an ABC")
        
        assert issubclass(IRagView, ABC), "IRagView is not an ABC"
        print("✓ IRagView is an ABC")
        
        assert issubclass(IChatView, ABC), "IChatView is not an ABC"
        print("✓ IChatView is an ABC")
        
        assert issubclass(IUIProvider, ABC), "IUIProvider is not an ABC"
        print("✓ IUIProvider is an ABC")
        
        return True
    except Exception as e:
        print(f"✗ ABC test failed: {e}")
        return False


def test_textual_available():
    """Test that Textual is available."""
    print("\nTesting Textual availability...")
    
    try:
        import textual
        print(f"✓ Textual version: {textual.__version__}")
        
        from textual.app import App
        print("✓ Textual App available")
        
        from textual.screen import Screen
        print("✓ Textual Screen available")
        
        return True
    except Exception as e:
        print(f"✗ Textual test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AgentX TUI Infrastructure Test")
    print("=" * 60)
    
    tests = [
        ("Textual Available", test_textual_available),
        ("Imports", test_imports),
        ("Provider Registry", test_provider_registry),
        ("Interface ABCs", test_interface_abc),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! TUI infrastructure is ready.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())