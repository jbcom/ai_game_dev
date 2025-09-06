"""E2E test runner for all game engines."""
import pytest
import sys
from pathlib import Path


def run_all_e2e_tests():
    """Run all E2E tests and generate comprehensive reports."""
    print("🚀 Starting AI Game Dev E2E Test Suite")
    print("=" * 50)
    
    # Configure pytest for E2E tests
    pytest_args = [
        "-v",  # Verbose output
        "-s",  # Don't capture output
        "-m", "e2e",  # Only run E2E tests
        "--tb=short",  # Short traceback format
        "tests/e2e/",  # E2E test directory
    ]
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    print("=" * 50)
    if exit_code == 0:
        print("✅ All E2E tests passed!")
    else:
        print("❌ Some E2E tests failed!")
    
    return exit_code


def run_single_engine_test(engine: str):
    """Run E2E tests for a specific engine."""
    engine_file_map = {
        "pygame": "test_pygame_e2e.py",
        "bevy": "test_bevy_e2e.py", 
        "godot": "test_godot_e2e.py",
        "arcade": "test_arcade_e2e.py"
    }
    
    if engine not in engine_file_map:
        print(f"❌ Unknown engine: {engine}")
        print(f"Available engines: {', '.join(engine_file_map.keys())}")
        return 1
    
    test_file = f"tests/e2e/{engine_file_map[engine]}"
    
    print(f"🎮 Running {engine.title()} E2E tests...")
    
    pytest_args = [
        "-v", "-s", "-m", "e2e",
        test_file
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific engine tests
        engine = sys.argv[1].lower()
        exit_code = run_single_engine_test(engine)
    else:
        # Run all E2E tests
        exit_code = run_all_e2e_tests()
    
    sys.exit(exit_code)