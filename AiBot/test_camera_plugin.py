#!/home/spark/RR2025/AiBot/venv/bin/python3
"""
Camera Plugin Test Script for AiBot
Tests the camera control plugin with various camera operations
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aibot.hardware.camera_controller import CameraPanTiltController
from aibot.plugins.camera_plugin import CameraControlPlugin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_camera_plugin():
    """Test the camera control plugin comprehensively."""
    print("🎬 Starting Camera Plugin Test")
    print("=" * 50)
    
    test_results = []
    
    try:
        # Initialize camera controller and plugin
        print("🔧 Initializing camera controller and plugin...")
        camera_controller = CameraPanTiltController()
        camera_plugin = CameraControlPlugin(camera_controller)
        
        # Test 1: Center Camera
        print("\n🎯 Test 1: Center Camera")
        result = await camera_plugin.center_camera()
        print(f"Result: {result}")
        test_results.append(("Center Camera", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 2: Get Camera Position
        print("\n📍 Test 2: Get Camera Position")
        result = camera_plugin.get_camera_position()
        print(f"Result: {result}")
        test_results.append(("Get Position", "✅" if "position" in result else "❌"))
        await asyncio.sleep(0.5)
        
        # Test 3: Pan to Specific Angle
        print("\n↔️ Test 3: Pan to 45 degrees")
        result = await camera_plugin.pan_to_angle(45)
        print(f"Result: {result}")
        test_results.append(("Pan to Angle", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 4: Tilt to Specific Angle
        print("\n↕️ Test 4: Tilt to 135 degrees")
        result = await camera_plugin.tilt_to_angle(135)
        print(f"Result: {result}")
        test_results.append(("Tilt to Angle", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 5: Set Camera Position
        print("\n🎯 Test 5: Set position to pan=120°, tilt=60°")
        result = await camera_plugin.set_camera_position(120, 60)
        print(f"Result: {result}")
        test_results.append(("Set Position", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 6: Relative Pan
        print("\n➡️ Test 6: Pan right by 30 degrees")
        result = await camera_plugin.pan_relative(30)
        print(f"Result: {result}")
        test_results.append(("Pan Relative", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 7: Relative Tilt
        print("\n⬆️ Test 7: Tilt up by 20 degrees")
        result = await camera_plugin.tilt_relative(20)
        print(f"Result: {result}")
        test_results.append(("Tilt Relative", "✅" if "successfully" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 8: Pan Sweep
        print("\n🔄 Test 8: Pan sweep from 30° to 150°")
        result = await camera_plugin.pan_sweep(30, 150, 2.0)
        print(f"Result: {result}")
        test_results.append(("Pan Sweep", "✅" if "completed" in result else "❌"))
        await asyncio.sleep(0.5)
        
        # Test 9: Tilt Sweep
        print("\n🔄 Test 9: Tilt sweep from 60° to 120°")
        result = await camera_plugin.tilt_sweep(60, 120, 2.0)
        print(f"Result: {result}")
        test_results.append(("Tilt Sweep", "✅" if "completed" in result else "❌"))
        await asyncio.sleep(0.5)
        
        # Test 10: Track Target
        print("\n🎯 Test 10: Track target at pan=90°, tilt=90° with normal speed")
        result = await camera_plugin.track_target(90, 90, "normal")
        print(f"Result: {result}")
        test_results.append(("Track Target", "✅" if "tracked" in result else "❌"))
        await asyncio.sleep(1)
        
        # Test 11: Security Scan
        print("\n🛡️ Test 11: Security scan at normal speed")
        result = await camera_plugin.security_scan("normal")
        print(f"Result: {result}")
        test_results.append(("Security Scan", "✅" if "completed" in result else "❌"))
        await asyncio.sleep(0.5)
        
        # Final position check
        print("\n📍 Final: Get final camera position")
        result = camera_plugin.get_camera_position()
        print(f"Final position: {result}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        test_results.append(("Exception", f"❌ {e}"))
    
    finally:
        # Cleanup
        if 'camera_controller' in locals():
            camera_controller.cleanup()
    
    # Print test results
    print("\n" + "=" * 50)
    print("🧪 CAMERA PLUGIN TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, status in test_results:
        print(f"{status} {test_name}")
        if status.startswith("✅"):
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Camera plugin is operational")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Check the output above.")


async def test_agent_integration():
    """Test camera plugin integration with the agent."""
    print("\n🤖 Testing Agent Integration")
    print("=" * 30)
    
    try:
        from aibot.agents.ollama_agent import OllamaBotAgent
        
        print("Initializing agent with camera plugin...")
        agent = OllamaBotAgent()
        
        if await agent.initialize():
            print("✅ Agent initialized successfully with camera plugin")
            
            # Test a few commands
            test_commands = [
                "center the camera",
                "pan the camera to 45 degrees",
                "get camera position",
                "perform a security scan"
            ]
            
            for command in test_commands:
                print(f"\n🗣️ Command: {command}")
                try:
                    response = await agent.process_command(command)
                    print(f"📱 Response: {response[:200]}...")  # Truncate long responses
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            agent.cleanup()
            print("\n✅ Agent integration test completed")
        else:
            print("❌ Failed to initialize agent")
            
    except ImportError as e:
        print(f"⚠️ Agent integration test skipped: {e}")
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")


async def main():
    """Main test function."""
    print("🎬 AiBot Camera Plugin Comprehensive Test")
    print("🤖 Testing camera pan-tilt control plugin functionality")
    print("📅 Test Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Run camera plugin tests
    await test_camera_plugin()
    
    # Run agent integration tests
    await test_agent_integration()
    
    print("\n🎬 All tests completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
