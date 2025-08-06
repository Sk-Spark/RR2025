#!/usr/bin/env python3
"""
AI Bot Agent for DummyAiBot - Testing with Orchestrator or Terminal Mode
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from config.settings import BotConfig
from communication.protocol import (
    Message, MessageType, TaskRequestMessage, TaskResponseMessage, 
    TaskStatus, StatusUpdateMessage
)
from agents.llm_service import LLMService
from controllers.movement_controller import MovementController
from controllers.camera_controller import CameraController

logger = logging.getLogger(__name__)


class DummyAiBot:
    """AI Bot Agent for testing with orchestrator or terminal mode"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.bot_id = config.agent_id
        self.status = "initializing"
        self.current_task = None
        
        # Initialize components
        # Only initialize orchestrator client if not in terminal mode
        if not config.terminal_mode:
            from communication.orchestrator_client import OrchestratorClient
            self.orchestrator_client = OrchestratorClient(config, self._handle_message)
        else:
            self.orchestrator_client = None
            
        self.llm_service = LLMService(config)
        self.movement_controller = MovementController(config)
        self.camera_controller = CameraController(config)
        
        # Task tracking
        self.active_tasks = {}
        self.task_history = []
        
        logger.info(f"Dummy AI Bot {self.bot_id} initialized")
    
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            logger.info("Initializing bot components...")
            
            # Initialize LLM service
            if not await self.llm_service.initialize():
                logger.warning("LLM service initialization failed - continuing without LLM")
            
            self.status = "ready"
            logger.info("Bot initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during bot initialization: {e}")
            self.status = "error"
            return False
    
    async def start(self):
        """Start the bot in orchestrator or terminal mode"""
        try:
            if self.config.terminal_mode:
                logger.info("Starting Dummy AI Bot in TERMINAL MODE...")
                await self._start_terminal_mode()
            else:
                logger.info("Starting Dummy AI Bot in ORCHESTRATOR MODE...")
                await self._start_orchestrator_mode()
                
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            self.status = "error"
    
    async def _start_orchestrator_mode(self):
        """Start in orchestrator mode (original behavior)"""
        if not self.orchestrator_client:
            logger.error("Orchestrator client not initialized")
            self.status = "error"
            return
            
        # Connect to orchestrator
        if await self.orchestrator_client.connect():
            # Send initial status
            await self.orchestrator_client.send_status_update("ready", None)
            
            # Start listening for messages
            await self.orchestrator_client.listen()
        else:
            logger.error("Failed to connect to orchestrator")
            self.status = "disconnected"
    
    async def _start_terminal_mode(self):
        """Start in terminal mode - accept commands from console"""
        print("\n" + "="*60)
        print("** DUMMY AI BOT - TERMINAL MODE **")
        print("="*60)
        print("Bot is now ready to accept commands from terminal!")
        print("Type 'help' for available commands or 'quit' to exit.")
        print("="*60 + "\n")
        
        self.status = "ready"
        
        while True:
            try:
                # Get user input
                user_input = input("Bot > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("** Shutting down bot...")
                    break
                
                if user_input.lower() == 'help':
                    self._show_terminal_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_bot_status()
                    continue
                
                # Process the command
                await self._process_terminal_command(user_input)
                
            except KeyboardInterrupt:
                print("\n** Received Ctrl+C, shutting down...")
                break
            except EOFError:
                print("\n** Input ended, shutting down...")
                break
            except Exception as e:
                print(f"ERROR: Error processing command: {e}")
                logger.error(f"Terminal command error: {e}")
    
    def _show_terminal_help(self):
        """Show available terminal commands"""
        print("\nAVAILABLE COMMANDS:")
        print("-" * 50)
        print("System Commands:")
        print("  help           - Show this help message")
        print("  status         - Show bot status")
        print("  quit/exit/q    - Exit the bot")
        print("\nMovement Commands:")
        print("  move forward [seconds]    - Move forward (default 1s)")
        print("  move backward [seconds]   - Move backward (default 1s)")
        print("  turn left [seconds]       - Turn left (default 0.5s)")
        print("  turn right [seconds]      - Turn right (default 0.5s)")
        print("\nCamera Commands:")
        print("  camera center             - Center camera")
        print("  camera pan left [degrees] - Pan camera left")
        print("  camera pan right [degrees]- Pan camera right")
        print("  camera tilt up [degrees]  - Tilt camera up")
        print("  camera tilt down [degrees]- Tilt camera down")
        print("  camera scan [range] [steps] - Scan area")
        print("\nComplex Tasks:")
        print("  scan area                 - Perform 360° scan")
        print("  patrol [points] [duration]- Patrol with N points")
        print("\nNatural Language:")
        print("  Just type what you want the bot to do!")
        print("  Example: 'look around and then move forward'")
        print("-" * 50 + "\n")
    
    def _show_bot_status(self):
        """Show current bot status in terminal"""
        status = self.get_status()
        print("\nBOT STATUS:")
        print("-" * 40)
        print(f"Bot ID: {status['bot_id']}")
        print(f"Status: {status['status']}")
        print(f"Current Task: {status['current_task'] or 'None'}")
        print(f"Active Tasks: {status['active_tasks']}")
        print(f"Completed Tasks: {status['completed_tasks']}")
        print(f"Capabilities: {', '.join(status['capabilities']) if status['capabilities'] else 'None'}")
        print(f"\nMovement Status: {status['movement_status']['status']}")
        print(f"Position: {status['movement_status']['current_position']}")
        print(f"\nCamera Status: {status['camera_status']['status']}")
        print(f"Pan: {status['camera_status']['pan_angle']}°, Tilt: {status['camera_status']['tilt_angle']}°")
        print("-" * 40 + "\n")
    
    async def _process_terminal_command(self, command: str):
        """Process a command from terminal input"""
        command = command.lower().strip()
        
        try:
            # Generate a unique task ID for terminal commands
            import uuid
            task_id = f"terminal_{uuid.uuid4().hex[:8]}"
            
            print(f"[Processing] {command}")
            
            # Parse and execute command
            if command.startswith('move '):
                await self._handle_terminal_movement(task_id, command)
            elif command.startswith('camera '):
                await self._handle_terminal_camera(task_id, command)
            elif command.startswith('scan'):
                await self._handle_terminal_scan(task_id, command)
            elif command.startswith('patrol'):
                await self._handle_terminal_patrol(task_id, command)
            else:
                # Natural language command - use LLM
                await self._handle_terminal_natural_language(task_id, command)
                
        except Exception as e:
            print(f"❌ Command failed: {e}")
            logger.error(f"Terminal command failed: {e}")
    
    async def _handle_terminal_movement(self, task_id: str, command: str):
        """Handle movement commands from terminal"""
        parts = command.split()
        
        if len(parts) < 2:
            print("❌ Invalid movement command")
            return
        
        direction = parts[1]
        duration = float(parts[2]) if len(parts) > 2 else 1.0
        
        parameters = {'direction': direction, 'duration': duration}
        result = await self._execute_movement_task(command, parameters)
        
        if result['success']:
            print(f"[COMPLETED] Movement: {result['action']}")
            print(f"[POSITION] New position: {result['final_position']}")
        else:
            print(f"❌ Movement failed")
    
    async def _handle_terminal_camera(self, task_id: str, command: str):
        """Handle camera commands from terminal"""
        parts = command.split()
        
        if len(parts) < 2:
            print("❌ Invalid camera command")
            return
        
        if parts[1] == 'center':
            parameters = {'action': 'center'}
        elif parts[1] == 'pan' and len(parts) >= 3:
            direction = parts[2]  # left or right
            degrees = float(parts[3]) if len(parts) > 3 else 15
            parameters = {'action': f'pan_{direction}', 'degrees': degrees}
        elif parts[1] == 'tilt' and len(parts) >= 3:
            direction = parts[2]  # up or down
            degrees = float(parts[3]) if len(parts) > 3 else 15
            parameters = {'action': f'tilt_{direction}', 'degrees': degrees}
        elif parts[1] == 'scan':
            scan_range = float(parts[2]) if len(parts) > 2 else 60
            steps = int(parts[3]) if len(parts) > 3 else 5
            parameters = {'action': 'scan', 'range': scan_range, 'steps': steps}
        else:
            print("❌ Invalid camera command")
            return
        
        result = await self._execute_camera_task(command, parameters)
        
        if result['success']:
            print(f"[COMPLETED] Camera action: {result['action']}")
            print(f"[CAMERA] Position: {result['camera_position']}")
        else:
            print(f"❌ Camera action failed")
    
    async def _handle_terminal_scan(self, task_id: str, command: str):
        """Handle scan commands from terminal"""
        parts = command.split()
        parameters = {}
        
        if len(parts) > 1 and parts[1] == 'area':
            parameters = {'scan_type': '360_degree'}
        
        print("🔍 Starting area scan...")
        result = await self._execute_scan_task(command, parameters)
        
        if result['success']:
            print(f"[COMPLETED] Scan: {result['scan_type']}")
            print(f"[DATA] Scan points: {len(result['scan_results'])}")
        else:
            print(f"❌ Scan failed")
    
    async def _handle_terminal_patrol(self, task_id: str, command: str):
        """Handle patrol commands from terminal"""
        parts = command.split()
        
        points = int(parts[1]) if len(parts) > 1 else 4
        duration = float(parts[2]) if len(parts) > 2 else 2.0
        
        parameters = {'points': points, 'duration': duration}
        
        print(f"[PATROL] Starting patrol with {points} points...")
        result = await self._execute_patrol_task(command, parameters)
        
        if result['success']:
            print(f"[COMPLETED] Patrol: {points} points")
            print(f"[LOG] Patrol entries: {len(result['patrol_log'])}")
        else:
            print(f"❌ Patrol failed")
    
    async def _handle_terminal_natural_language(self, task_id: str, command: str):
        """Handle natural language commands using LLM"""
        print("🧠 Analyzing command with LLM...")
        
        # Use LLM to analyze the command
        task_analysis = await self.llm_service.analyze_task(command, self.config.capabilities)
        
        if not task_analysis or not task_analysis.get('feasible', False):
            print("❌ Could not understand the command or task is not feasible. Try being more specific or use 'help'.")
            return
        
        # Determine task type based on required capabilities
        required_caps = task_analysis.get('required_capabilities', [])
        task_type = 'general'
        if 'movement_simulation' in required_caps:
            task_type = 'movement'
        elif 'camera_simulation' in required_caps:
            task_type = 'camera'
        
        print(f"🔍 LLM Analysis: {task_type} task")
        
        # Show response if available (for capability questions)
        if 'response' in task_analysis:
            print(f"🤖 {task_analysis['response']}")
            print(f"[COMPLETED] Task completed successfully!")
            return
        
        print(f"💭 Understanding: {task_analysis.get('llm_response', 'Processing...')}")
        print(f"📋 Execution steps: {', '.join(task_analysis.get('execution_steps', []))}")
        
        parameters = task_analysis.get('parameters', {})
        result = await self._execute_generic_task(command, parameters, task_analysis)
        
        if result['success']:
            print(f"[COMPLETED] Task completed successfully!")
            print(f"[ACTIONS] Actions taken: {', '.join(result.get('executed_actions', []))}")
        else:
            print(f"❌ Task failed")
    
    async def shutdown(self):
        """Shutdown the bot gracefully"""
        try:
            logger.info("Shutting down Dummy AI Bot...")
            
            self.status = "shutting_down"
            
            # Cancel any active tasks
            for task_id in list(self.active_tasks.keys()):
                await self._cancel_task(task_id)
            
            # Cleanup components
            await self.llm_service.cleanup()
            self.movement_controller.cleanup()
            self.camera_controller.cleanup()
            
            # Disconnect from orchestrator (if connected)
            if self.orchestrator_client:
                await self.orchestrator_client.disconnect()
            
            self.status = "stopped"
            logger.info("Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _handle_message(self, message: Message):
        """Handle incoming messages from orchestrator"""
        try:
            logger.info(f"Handling message type: {message.message_type.value}")
            
            if message.message_type == MessageType.TASK_REQUEST:
                await self._handle_task_request(message)
            elif message.message_type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(message)
            else:
                logger.info(f"Unhandled message type: {message.message_type.value}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_task_request(self, message: Message):
        """Handle task request from orchestrator"""
        try:
            task_data = message.data
            task_id = task_data.get('task_id')
            task_type = task_data.get('task_type')
            task_description = task_data.get('task_description')
            parameters = task_data.get('parameters', {})
            
            logger.info(f"Received task {task_id}: {task_description}")
            
            # Add to active tasks
            self.active_tasks[task_id] = {
                'task_id': task_id,
                'task_type': task_type,
                'description': task_description,
                'parameters': parameters,
                'status': TaskStatus.IN_PROGRESS,
                'start_time': datetime.utcnow().isoformat()
            }
            
            # Update current task
            self.current_task = task_id
            if self.orchestrator_client:
                await self.orchestrator_client.send_status_update("busy", task_id)
            
            # Execute task
            await self._execute_task(task_id, task_type, task_description, parameters)
            
        except Exception as e:
            logger.error(f"Error handling task request: {e}")
            if task_id:
                await self._send_task_failure(task_id, str(e))
    
    async def _execute_task(self, task_id: str, task_type: str, description: str, parameters: Dict[str, Any]):
        """Execute a task based on type and description"""
        try:
            logger.info(f"Executing task {task_id}: {description}")
            
            # Analyze task with LLM (if available)
            task_analysis = await self.llm_service.analyze_task(description, self.config.capabilities)
            logger.info(f"Task analysis: {task_analysis}")
            
            # Execute based on task type
            if task_type == "movement":
                result = await self._execute_movement_task(description, parameters)
            elif task_type == "camera":
                result = await self._execute_camera_task(description, parameters)
            elif task_type == "scan":
                result = await self._execute_scan_task(description, parameters)
            elif task_type == "patrol":
                result = await self._execute_patrol_task(description, parameters)
            else:
                result = await self._execute_generic_task(description, parameters, task_analysis)
            
            # Send success response
            await self._send_task_completion(task_id, result)
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            await self._send_task_failure(task_id, str(e))
    
    async def _execute_movement_task(self, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute movement-related tasks (SIMULATION ONLY)"""
        direction = parameters.get('direction', 'forward')
        duration = parameters.get('duration', 1.0)
        
        logger.info(f"SIMULATING movement: {direction} for {duration}s (NO HARDWARE)")
        
        if direction == 'forward':
            success = await self.movement_controller.move_forward(duration)
        elif direction == 'backward':
            success = await self.movement_controller.move_backward(duration)
        elif direction == 'left':
            success = await self.movement_controller.turn_left(duration)
        elif direction == 'right':
            success = await self.movement_controller.turn_right(duration)
        else:
            success = False
        
        return {
            'success': success,
            'action': f"SIMULATED {direction} movement",
            'duration': duration,
            'final_position': self.movement_controller.get_position(),
            'note': 'Pure simulation - no actual hardware movement'
        }
    
    async def _execute_camera_task(self, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute camera-related tasks (SIMULATION ONLY)"""
        action = parameters.get('action', 'center')
        
        logger.info(f"SIMULATING camera action: {action} (NO HARDWARE)")
        
        if action == 'center':
            success = await self.camera_controller.center_camera()
        elif action == 'pan_left':
            degrees = parameters.get('degrees', 15)
            success = await self.camera_controller.pan_left(degrees)
        elif action == 'pan_right':
            degrees = parameters.get('degrees', 15)
            success = await self.camera_controller.pan_right(degrees)
        elif action == 'tilt_up':
            degrees = parameters.get('degrees', 15)
            success = await self.camera_controller.tilt_up(degrees)
        elif action == 'tilt_down':
            degrees = parameters.get('degrees', 15)
            success = await self.camera_controller.tilt_down(degrees)
        elif action == 'scan':
            scan_range = parameters.get('range', 60)
            steps = parameters.get('steps', 5)
            success = await self.camera_controller.scan_area(scan_range, steps)
        else:
            success = False
        
        return {
            'success': success,
            'action': f"SIMULATED {action}",
            'camera_position': self.camera_controller.get_camera_position(),
            'note': 'Pure simulation - no actual camera movement'
        }
    
    async def _execute_scan_task(self, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scanning tasks (SIMULATION ONLY - camera + movement)"""
        logger.info("SIMULATING scan task (NO HARDWARE)")
        
        # Center camera first
        await self.camera_controller.center_camera()
        
        # Perform 360-degree scan
        scan_results = []
        for angle in [0, 90, 180, 270]:
            # Turn to angle
            await self.movement_controller.turn_right(0.25)  # 90 degrees
            
            # Camera scan at this position
            await self.camera_controller.scan_area(90, 3)
            
            scan_results.append({
                'heading': angle,
                'camera_scan': 'simulated_completed',
                'position': self.movement_controller.get_position()
            })
            
            await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'scan_type': 'simulated_360_degree',
            'scan_results': scan_results,
            'note': 'Pure simulation - no actual scanning'
        }
    
    async def _execute_patrol_task(self, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patrol tasks (SIMULATION ONLY)"""
        logger.info("SIMULATING patrol task (NO HARDWARE)")
        
        patrol_points = parameters.get('points', 4)
        duration_per_point = parameters.get('duration', 2.0)
        
        patrol_log = []
        
        for i in range(patrol_points):
            # Move forward
            await self.movement_controller.move_forward(duration_per_point)
            
            # Look around
            await self.camera_controller.scan_area(180, 3)
            
            # Log patrol point
            patrol_log.append({
                'point': i + 1,
                'position': self.movement_controller.get_position(),
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'simulated_patrol_point'
            })
            
            # Turn for next point
            if i < patrol_points - 1:
                await self.movement_controller.turn_right(0.25)  # 90 degrees
        
        return {
            'success': True,
            'patrol_points': patrol_points,
            'patrol_log': patrol_log,
            'note': 'Pure simulation - no actual patrol movement'
        }
    
    async def _execute_generic_task(self, description: str, parameters: Dict[str, Any], 
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic tasks using LLM analysis (SIMULATION ONLY)"""
        logger.info(f"SIMULATING generic task: {description} (NO HARDWARE)")
        
        # Generate action plan with LLM
        action_plan = await self.llm_service.generate_action_plan(description, parameters)
        logger.info(f"Action plan: {action_plan}")
        
        # Simulate task execution based on required capabilities
        required_caps = analysis.get('required_capabilities', [])
        executed_actions = []
        
        for capability in required_caps:
            if capability == "movement" or capability == "movement_simulation":
                await self.movement_controller.move_forward(1.0)
                executed_actions.append("simulated_movement_forward")
            elif capability == "camera_control" or capability == "camera_simulation":
                await self.camera_controller.center_camera()
                executed_actions.append("simulated_camera_centered")
        
        # Add some delay to simulate processing
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'task_description': description,
            'action_plan': action_plan,
            'executed_actions': executed_actions,
            'analysis': analysis,
            'note': 'Pure simulation - no actual hardware actions'
        }
    
    async def _send_task_completion(self, task_id: str, result: Dict[str, Any]):
        """Send task completion response"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = TaskStatus.COMPLETED
            self.active_tasks[task_id]['end_time'] = datetime.utcnow().isoformat()
            self.active_tasks[task_id]['result'] = result
            
            # Move to history
            self.task_history.append(self.active_tasks.pop(task_id))
        
        if self.orchestrator_client:
            await self.orchestrator_client.send_task_response(
                task_id, TaskStatus.COMPLETED.value, result
            )
            
            self.current_task = None
            await self.orchestrator_client.send_status_update("ready", None)
        
        logger.info(f"Task {task_id} completed successfully")
    
    async def _send_task_failure(self, task_id: str, error_message: str):
        """Send task failure response"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = TaskStatus.FAILED
            self.active_tasks[task_id]['end_time'] = datetime.utcnow().isoformat()
            self.active_tasks[task_id]['error'] = error_message
            
            # Move to history
            self.task_history.append(self.active_tasks.pop(task_id))
        
        if self.orchestrator_client:
            await self.orchestrator_client.send_task_response(
                task_id, TaskStatus.FAILED.value, None, error_message
            )
            
            self.current_task = None
            await self.orchestrator_client.send_status_update("ready", None)
        
        logger.error(f"Task {task_id} failed: {error_message}")
    
    async def _cancel_task(self, task_id: str):
        """Cancel an active task"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = TaskStatus.CANCELLED
            self.active_tasks[task_id]['end_time'] = datetime.utcnow().isoformat()
            
            # Move to history
            self.task_history.append(self.active_tasks.pop(task_id))
            
            logger.info(f"Task {task_id} cancelled")
    
    async def _handle_heartbeat(self, message: Message):
        """Handle heartbeat message"""
        logger.debug("Heartbeat received from orchestrator")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'bot_id': self.bot_id,
            'status': self.status,
            'current_task': self.current_task,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.task_history),
            'capabilities': self.config.capabilities,
            'movement_status': self.movement_controller.get_status(),
            'camera_status': self.camera_controller.get_status(),
            'timestamp': datetime.utcnow().isoformat()
        }
