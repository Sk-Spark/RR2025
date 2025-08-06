#!/usr/bin/env /home/spark/.venv/bin/python
"""
Simple test script to verify the orchestrator setup.
Tests basic functionality and checks all components.
"""

import asyncio
import sys
import subprocess
from pathlib import Path
import importlib.util
import json
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class OrchestratorTest:
    """
    Test suite for the orchestrator system.
    """
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = 0
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log a test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
        if not success:
            self.failed_tests += 1
    
    def test_python_environment(self):
        """Test Python environment and virtual environment."""
        print("🐍 Testing Python Environment")
        print("-" * 40)
        
        # Check Python version
        version_info = sys.version_info
        python_ok = version_info.major == 3 and version_info.minor >= 11
        self.log_test(
            "Python Version (>=3.11)",
            python_ok,
            f"Found Python {version_info.major}.{version_info.minor}.{version_info.micro}"
        )
        
        # Check virtual environment
        venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        self.log_test(
            "Virtual Environment Active",
            venv_active,
            f"Virtual env: {sys.prefix}" if venv_active else "No virtual environment detected"
        )
        
        # Check if we're using the correct venv
        expected_venv = "/home/spark/.venv"
        correct_venv = expected_venv in sys.prefix
        self.log_test(
            "Correct Virtual Environment",
            correct_venv,
            f"Expected: {expected_venv}, Got: {sys.prefix}"
        )
    
    def test_required_packages(self):
        """Test if required packages are available."""
        print("\n📦 Testing Required Packages")
        print("-" * 40)
        
        required_packages = [
            ("semantic_kernel", "semantic-kernel"),
            ("websockets", "websockets"),
            ("aiohttp", "aiohttp"),
            ("pydantic", "pydantic"),
            ("ollama", "ollama"),
            ("yaml", "PyYAML")
        ]
        
        for module_name, package_name in required_packages:
            try:
                spec = importlib.util.find_spec(module_name)
                available = spec is not None
                self.log_test(
                    f"Package: {package_name}",
                    available,
                    f"Module '{module_name}' found" if available else f"Module '{module_name}' not found"
                )
            except Exception as e:
                self.log_test(
                    f"Package: {package_name}",
                    False,
                    f"Error checking module: {e}"
                )
    
    def test_project_structure(self):
        """Test project structure and files."""
        print("\n📁 Testing Project Structure")
        print("-" * 40)
        
        base_path = Path(__file__).parent
        
        required_files = [
            "main.py",
            "example_agent.py",
            "cli_tool.py",
            "requirements.txt",
            ".env",
            "README.md"
        ]
        
        required_dirs = [
            "src",
            "src/core",
            "src/agents", 
            "src/communication",
            "src/planner",
            "src/integrations",
            "src/utils",
            "config",
            "logs"
        ]
        
        # Check files
        for file_name in required_files:
            file_path = base_path / file_name
            exists = file_path.exists()
            self.log_test(
                f"File: {file_name}",
                exists,
                f"Found at {file_path}" if exists else f"Missing: {file_path}"
            )
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.log_test(
                f"Directory: {dir_name}",
                exists,
                f"Found at {dir_path}" if exists else f"Missing: {dir_path}"
            )
    
    def test_configuration(self):
        """Test configuration loading."""
        print("\n⚙️ Testing Configuration")
        print("-" * 40)
        
        try:
            from config.config import ConfigManager
            
            config_manager = ConfigManager()
            config = config_manager.config
            
            self.log_test(
                "Configuration Loading",
                True,
                "Configuration loaded successfully"
            )
            
            # Test specific config values
            websocket_config_ok = hasattr(config, 'websocket') and hasattr(config.websocket, 'port')
            self.log_test(
                "WebSocket Configuration",
                websocket_config_ok,
                f"WebSocket port: {config.websocket.port if websocket_config_ok else 'N/A'}"
            )
            
            ollama_config_ok = hasattr(config, 'ollama') and hasattr(config.ollama, 'model')
            self.log_test(
                "Ollama Configuration",
                ollama_config_ok,
                f"Ollama model: {config.ollama.model if ollama_config_ok else 'N/A'}"
            )
            
        except Exception as e:
            self.log_test(
                "Configuration Loading",
                False,
                f"Error: {e}"
            )
    
    def test_core_imports(self):
        """Test core module imports."""
        print("\n🔧 Testing Core Imports")
        print("-" * 40)
        
        core_modules = [
            ("src.core.models", "Core Models"),
            ("src.agents.agent_manager", "Agent Manager"),
            ("src.agents.task_manager", "Task Manager"),
            ("src.communication.websocket_server", "WebSocket Server"),
            ("src.utils.logging_utils", "Logging Utils"),
            ("src.utils.helpers", "Helper Functions")
        ]
        
        for module_name, display_name in core_modules:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.log_test(
                        f"Import: {display_name}",
                        True,
                        f"Successfully imported {module_name}"
                    )
                else:
                    self.log_test(
                        f"Import: {display_name}",
                        False,
                        f"Module {module_name} not found"
                    )
            except Exception as e:
                self.log_test(
                    f"Import: {display_name}",
                    False,
                    f"Import error: {e}"
                )
    
    def test_ollama_connection(self):
        """Test Ollama connection."""
        print("\n🧠 Testing Ollama Connection")
        print("-" * 40)
        
        try:
            # Test if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            ollama_running = response.status_code == 200
            
            if ollama_running:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                llama_available = any("llama" in name.lower() for name in model_names)
                
                self.log_test(
                    "Ollama Service",
                    True,
                    f"Service running, {len(models)} models available"
                )
                
                self.log_test(
                    "LLaMA Model Available",
                    llama_available,
                    f"Available models: {', '.join(model_names[:3])}" + ("..." if len(model_names) > 3 else "")
                )
            else:
                self.log_test(
                    "Ollama Service",
                    False,
                    f"HTTP {response.status_code} from Ollama API"
                )
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Ollama Service",
                False,
                "Connection refused - Ollama not running"
            )
        except Exception as e:
            self.log_test(
                "Ollama Service",
                False,
                f"Error: {e}"
            )
    
    async def test_orchestrator_startup(self):
        """Test if orchestrator can start up (dry run)."""
        print("\n🚀 Testing Orchestrator Startup")
        print("-" * 40)
        
        try:
            from src.orchestrator import Orchestrator
            from config.config import ConfigManager
            
            # Test configuration
            config_manager = ConfigManager()
            
            # Test orchestrator creation (don't actually start it)
            orchestrator = Orchestrator(config_manager)
            
            self.log_test(
                "Orchestrator Creation",
                True,
                "Orchestrator instance created successfully"
            )
            
            # Test component initialization
            components_ok = all([
                hasattr(orchestrator, 'agent_manager'),
                hasattr(orchestrator, 'task_manager'),
                hasattr(orchestrator, 'websocket_server')
            ])
            
            self.log_test(
                "Component Initialization",
                components_ok,
                "All core components initialized"
            )
            
        except Exception as e:
            self.log_test(
                "Orchestrator Creation",
                False,
                f"Error: {e}"
            )
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = total_tests - self.failed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed:      {passed_tests} ✅")
        print(f"Failed:      {self.failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 All tests passed! The orchestrator setup looks good.")
            print("\n🚀 You can now start the orchestrator with:")
            print("   source /home/spark/.venv/bin/activate")
            print("   python main.py")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Please address the issues above.")
            
            # Provide specific guidance based on failed tests
            failed_test_names = [test["test"] for test in self.test_results if not test["success"]]
            
            if any("Package:" in test for test in failed_test_names):
                print("\n💡 To install missing packages:")
                print("   source /home/spark/.venv/bin/activate")
                print("   pip install -r requirements.txt")
            
            if "Ollama Service" in failed_test_names:
                print("\n💡 To start Ollama:")
                print("   ollama serve")
            
            if any("Virtual Environment" in test for test in failed_test_names):
                print("\n💡 To activate the virtual environment:")
                print("   source /home/spark/.venv/bin/activate")
        
        print("="*50)


async def main():
    """Main test runner."""
    print("🧪 Orchestrator Agent Test Suite")
    print("="*50)
    print("This test will verify your orchestrator setup is correct.")
    print()
    
    tester = OrchestratorTest()
    
    # Run all tests
    tester.test_python_environment()
    tester.test_required_packages()
    tester.test_project_structure()
    tester.test_configuration()
    tester.test_core_imports()
    tester.test_ollama_connection()
    await tester.test_orchestrator_startup()
    
    # Print summary
    tester.print_summary()
    
    # Return exit code
    return 0 if tester.failed_tests == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)
