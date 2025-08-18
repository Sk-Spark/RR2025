#!/usr/bin/env python3
"""
Ollama Agent Module
Main agent that uses Ollama and Semantic Kernel for LED and movement control.
"""

import json
import logging
import asyncio
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions import KernelArguments

from ..hardware.led_controller import LEDController
from ..plugins.led_plugin import LEDControlPlugin
from ..hardware.movement_controller import MovementController
from ..plugins.movement_plugin import MovementControlPlugin

logger = logging.getLogger(__name__)


class OllamaBotAgent:
    """Main agent that uses Ollama and Semantic Kernel for bot control (LED and movement)."""
    
    def __init__(self, model_name: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        """Initialize the Ollama bot agent."""
        self.model_name = model_name
        self.base_url = base_url
        self.kernel: Optional[sk.Kernel] = None
        self.led_controller: Optional[LEDController] = None
        self.led_plugin: Optional[LEDControlPlugin] = None
        self.movement_controller: Optional[MovementController] = None
        self.movement_plugin: Optional[MovementControlPlugin] = None
        
    async def initialize(self, led_pin: int = 18, motor_config: Optional[dict] = None) -> bool:
        """Initialize the agent with LED controller, movement controller, and Semantic Kernel."""
        try:
            # Initialize LED controller
            self.led_controller = LEDController(led_pin)
            
            # Initialize movement controller
            self.movement_controller = MovementController(motor_config=motor_config)
            
            # Initialize Semantic Kernel
            self.kernel = sk.Kernel()
            
            # Add Ollama chat completion service
            chat_completion = OllamaChatCompletion(
                ai_model_id=self.model_name
            )
            self.kernel.add_service(chat_completion)
            
            # Create and add LED control plugin
            self.led_plugin = LEDControlPlugin(self.led_controller)
            self.kernel.add_plugin(self.led_plugin, plugin_name="led_control")
            
            # Create and add movement control plugin
            self.movement_plugin = MovementControlPlugin(self.movement_controller)
            self.kernel.add_plugin(self.movement_plugin, plugin_name="movement_control")
            
            logger.info(f"Agent initialized with model {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def process_command(self, user_input: str) -> str:
        """Process user command through Ollama and execute control functions if needed."""
        try:
            # Build the prompt with movement functions
            movement_section = """
            You also have access to these movement control functions:
            - move_forward: Move the robot forward for 1 second
            - move_backward: Move the robot backward for 1 second
            - turn_left: Turn the robot left for 1 second
            - turn_right: Turn the robot right for 1 second
            - strafe_left: Move the robot sideways left for 1 second
            - strafe_right: Move the robot sideways right for 1 second
            - stop_robot: Stop all robot movement immediately
            - get_movement_status: Get the current movement status"""
            
            movement_commands = """
                - CALL_FUNCTION:move_forward
                - CALL_FUNCTION:move_backward  
                - CALL_FUNCTION:turn_left
                - CALL_FUNCTION:turn_right
                - CALL_FUNCTION:strafe_left
                - CALL_FUNCTION:strafe_right
                - CALL_FUNCTION:stop_robot
                - CALL_FUNCTION:get_movement_status"""
            
            # Create the prompt with template variable
            prompt_template = f"""You are a robot control assistant. 
            You are responsible for using the available functions to complete the task provided by user.

            Available LED Commands:
            - turn_led_on: Turn the LED on
            - turn_led_off: Turn the LED off
            - get_led_status: Get current LED status
            
            {movement_section}

            Available Movement Commands:
            - move_forward: Move robot forward for 1 second
            - move_backward: Move robot backward for 1 second
            - turn_left: Turn robot left for 1 second
            - turn_right: Turn robot right for 1 second
            - strafe_left: Move robot sideways left for 1 second
            - strafe_right: Move robot sideways right for 1 second
            - stop_robot: Stop all robot movement immediately
            - get_movement_status: Get current movement status

            CRITICAL INSTRUCTIONS:
            - When user requests robot actions, you MUST respond with ONLY a JSON object in the exact format shown below
            - Use function names exactly as listed above (without CALL_FUNCTION: prefix)
            - Do NOT provide explanations or additional text when giving function calls
            - If the user asks for information or conversation (not robot actions), respond with normal text

            JSON Response Format:
            {{
                "actions": [
                    {{"function": "function_name", "description": "brief description"}},
                    {{"function": "function_name", "description": "brief description"}}
                ]
            }}

            Examples:
            - For "turn on LED": {{"actions": [{{"function": "turn_led_on", "description": "Turn LED on"}}]}}
            - For "blink LED": 
              {{
                "actions": [
                    {{"function": "turn_led_on", "description": "Turn LED on"}},
                    {{"function": "turn_led_off", "description": "Turn LED off"}},
                    {{"function": "turn_led_on", "description": "Turn LED on"}},
                    {{"function": "turn_led_off", "description": "Turn LED off"}}
                ]
              }}
            - For "move forward then right": 
              {{
                "actions": [
                    {{"function": "move_forward", "description": "Move robot forward"}},
                    {{"function": "turn_right", "description": "Turn robot right"}}
                ]
              }}
            - For "make a square": 
              {{
                "actions": [
                    {{"function": "move_forward", "description": "Move forward - side 1"}},
                    {{"function": "turn_right", "description": "Turn right - corner 1"}},
                    {{"function": "move_forward", "description": "Move forward - side 2"}},
                    {{"function": "turn_right", "description": "Turn right - corner 2"}},
                    {{"function": "move_forward", "description": "Move forward - side 3"}},
                    {{"function": "turn_right", "description": "Turn right - corner 3"}},
                    {{"function": "move_forward", "description": "Move forward - side 4"}},
                    {{"function": "turn_right", "description": "Turn right - corner 4"}}
                ]
              }}

            User: {{{{$user_input}}}}

            Response:"""

            # Create and invoke the function
            decision_function = self.kernel.add_function(
                plugin_name="decision",
                function_name="decide_action",
                prompt=prompt_template,
                prompt_template_config=PromptTemplateConfig(
                    template=prompt_template,
                    name="decide_action",
                    description="Decide which function to call based on user input"
                )
            )
            
            # Get the LLM's decision
            arguments = KernelArguments(user_input=user_input)
            decision_result = await self.kernel.invoke(decision_function, arguments)
            decision = str(decision_result).strip()
            
            logger.info(f"LLM decision: {decision}")
            
            # Check if the response contains JSON actions
            if decision.strip().startswith('{') and '"actions"' in decision:
                return await self._execute_json_actions(decision)
            # Fallback: Check if the response contains legacy function calls
            elif "CALL_FUNCTION:" in decision:
                return await self._execute_function_calls(decision)
            else:
                # If the response doesn't contain proper function calls but mentions movement actions,
                # try to parse and convert them
                converted_decision = self._convert_text_to_function_calls(decision, user_input)
                if converted_decision:
                    logger.info(f"Converted decision: {converted_decision}")
                    return await self._execute_function_calls(converted_decision)
                else:
                    # Return the conversational response from the LLM
                    return decision
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I encountered an error processing your request: {e}"
    
    def _convert_text_to_function_calls(self, decision: str, user_input: str) -> str:
        """Convert text-based movement commands to proper function calls."""
        # Common patterns that indicate the user wants robot actions
        action_keywords = ["move", "turn", "go", "rotate", "strafe", "stop", "led", "light", "square", "circle", "pattern"]
        
        # Check if user input contains action keywords
        if not any(keyword in user_input.lower() for keyword in action_keywords):
            return ""
        
        # Dictionary to map text commands to function calls
        command_mapping = {
            "move_forward": "CALL_FUNCTION:move_forward",
            "move_backward": "CALL_FUNCTION:move_backward", 
            "turn_left": "CALL_FUNCTION:turn_left",
            "turn_right": "CALL_FUNCTION:turn_right",
            "strafe_left": "CALL_FUNCTION:strafe_left",
            "strafe_right": "CALL_FUNCTION:strafe_right",
            "stop_robot": "CALL_FUNCTION:stop_robot",
            "turn_led_on": "CALL_FUNCTION:turn_led_on",
            "turn_led_off": "CALL_FUNCTION:turn_led_off"
        }
        
        # Handle specific patterns like "make a square"
        if "square" in user_input.lower():
            # A square requires 4 forward movements and 4 right turns
            return "CALL_FUNCTION:move_forward;CALL_FUNCTION:turn_right;CALL_FUNCTION:move_forward;CALL_FUNCTION:turn_right;CALL_FUNCTION:move_forward;CALL_FUNCTION:turn_right;CALL_FUNCTION:move_forward;CALL_FUNCTION:turn_right"
        
        # Try to extract commands from the decision text
        converted_calls = []
        for text_cmd, func_call in command_mapping.items():
            if text_cmd in decision.lower().replace("_", " "):
                converted_calls.append(func_call)
        
        return ";".join(converted_calls) if converted_calls else ""

    async def _execute_json_actions(self, decision: str) -> str:
        """Execute actions from JSON response format."""
        try:
            # Parse the JSON response
            logger.info(f"Parsing JSON decision: {decision}")
            data = json.loads(decision)
            
            if "actions" not in data:
                return "Error: JSON response missing 'actions' field"
            
            actions = data["actions"]
            if not isinstance(actions, list):
                return "Error: 'actions' must be a list"
            
            if not actions:
                return "No actions to execute"
            
            results = []
            logger.info(f"Executing {len(actions)} JSON actions")
            
            for i, action in enumerate(actions, 1):
                try:
                    if not isinstance(action, dict):
                        error_msg = f"Step {i}: Error - action must be an object"
                        logger.error(error_msg)
                        results.append(error_msg)
                        continue
                    
                    function_name = action.get("function")
                    description = action.get("description", function_name)
                    
                    if not function_name:
                        error_msg = f"Step {i}: Error - missing function name"
                        logger.error(error_msg)
                        results.append(error_msg)
                        continue
                    
                    logger.info(f"Executing action {i}/{len(actions)}: {function_name} - {description}")
                    result = await self._execute_single_function_by_name(function_name)
                    results.append(f"Step {i} ({description}): {result}")
                    
                    # Add delay between actions for safety
                    if i < len(actions):
                        await asyncio.sleep(0.2)
                        
                except Exception as e:
                    error_msg = f"Step {i}: Error executing action - {e}"
                    logger.error(error_msg)
                    results.append(error_msg)
            
            return "\n".join(results)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return f"Error: Invalid JSON format - {e}"
        except Exception as e:
            logger.error(f"Error executing JSON actions: {e}")
            return f"Error executing actions: {e}"

    async def _execute_function_calls(self, decision: str) -> str:
        """Execute multiple function calls sequentially based on the LLM decision."""
        results = []
        
        # Debug: Log the raw decision
        logger.info(f"Raw decision for parsing: {repr(decision)}")
        
        # Check if we have multiple function calls by looking for semicolons or newlines
        if ';' in decision:
            # Split by semicolons
            function_calls = [call.strip() for call in decision.split(';') if 'CALL_FUNCTION:' in call]
            logger.info(f"Found {len(function_calls)} function calls by semicolon split")
        else:
            # Split by newlines and extract CALL_FUNCTION: lines
            lines = decision.split('\n')
            logger.info(f"Split by newlines into {len(lines)} lines: {lines}")
            function_calls = [line.strip() for line in lines if line.strip().startswith('CALL_FUNCTION:')]
            logger.info(f"Found {len(function_calls)} function calls by newline split: {function_calls}")
        
        # If still no function calls found, check if the decision itself is a single function call
        if not function_calls and 'CALL_FUNCTION:' in decision:
            function_calls = [decision.strip()]
            logger.info(f"Using entire decision as single function call: {function_calls}")
        
        if not function_calls:
            return "No valid function calls found in the response"
        
        logger.info(f"Executing {len(function_calls)} function call(s)")
        
        for i, call in enumerate(function_calls, 1):
            try:
                logger.info(f"Executing function call {i}/{len(function_calls)}: {call}")
                result = await self._execute_single_function(call)
                results.append(f"Step {i}: {result}")
                
                # Add a small delay between function calls for safety
                if i < len(function_calls):
                    await asyncio.sleep(0.2)
                    
            except Exception as e:
                error_msg = f"Step {i}: Error executing '{call}' - {e}"
                logger.error(error_msg)
                results.append(error_msg)
                # Continue with next function call even if one fails
        
        return "\n".join(results)
    
    async def _execute_single_function(self, call: str) -> str:
        """Execute a single function call and return the result."""
        # Parse the decision and call the appropriate function
        if "turn_led_on" in call:
            logger.info("Executing command: turn LED on")
            result = self.led_plugin.turn_led_on()
            return f"LED control executed: {result}"
        elif "turn_led_off" in call:
            logger.info("Executing command: turn LED off")
            result = self.led_plugin.turn_led_off()
            return f"LED control executed: {result}"
        elif "get_led_status" in call:
            logger.info("Executing command: get LED status")
            result = self.led_plugin.get_led_status()
            return f"LED status: {result}"
        elif "move_forward" in call:
            logger.info("Executing command: move forward")
            result = await self.movement_plugin.move_forward()
            return f"Movement executed: {result}"
        elif "move_backward" in call:
            logger.info("Executing command: move backward")
            result = await self.movement_plugin.move_backward()
            return f"Movement executed: {result}"
        elif "turn_left" in call:
            logger.info("Executing command: turn left")
            result = await self.movement_plugin.turn_left()
            return f"Movement executed: {result}"
        elif "turn_right" in call:
            logger.info("Executing command: turn right")
            result = await self.movement_plugin.turn_right()
            return f"Movement executed: {result}"
        elif "strafe_left" in call:
            logger.info("Executing command: strafe left")
            result = await self.movement_plugin.strafe_left()
            return f"Movement executed: {result}"
        elif "strafe_right" in call:
            logger.info("Executing command: strafe right")
            result = await self.movement_plugin.strafe_right()
            return f"Movement executed: {result}"
        elif "stop_robot" in call:
            logger.info("Executing command: stop robot")
            result = self.movement_plugin.stop_robot()
            return f"Movement executed: {result}"
        elif "get_movement_status" in call:
            logger.info("Executing command: get movement status")
            result = self.movement_plugin.get_movement_status()
            return f"Movement status: {result}"
        else:
            return f"Unknown function call: {call}"
    
    async def _execute_single_function_by_name(self, function_name: str) -> str:
        """Execute a single function by name and return the result."""
        # LED functions
        if function_name == "turn_led_on":
            logger.info("Executing JSON command: turn LED on")
            result = self.led_plugin.turn_led_on()
            return f"LED: {result}"
        elif function_name == "turn_led_off":
            logger.info("Executing JSON command: turn LED off")
            result = self.led_plugin.turn_led_off()
            return f"LED: {result}"
        elif function_name == "get_led_status":
            logger.info("Executing JSON command: get LED status")
            result = self.led_plugin.get_led_status()
            return f"LED status: {result}"
        
        # Movement functions
        elif function_name == "move_forward":
            logger.info("Executing JSON command: move forward")
            result = await self.movement_plugin.move_forward()
            return f"Movement: {result}"
        elif function_name == "move_backward":
            logger.info("Executing JSON command: move backward")
            result = await self.movement_plugin.move_backward()
            return f"Movement: {result}"
        elif function_name == "turn_left":
            logger.info("Executing JSON command: turn left")
            result = await self.movement_plugin.turn_left()
            return f"Movement: {result}"
        elif function_name == "turn_right":
            logger.info("Executing JSON command: turn right")
            result = await self.movement_plugin.turn_right()
            return f"Movement: {result}"
        elif function_name == "strafe_left":
            logger.info("Executing JSON command: strafe left")
            result = await self.movement_plugin.strafe_left()
            return f"Movement: {result}"
        elif function_name == "strafe_right":
            logger.info("Executing JSON command: strafe right")
            result = await self.movement_plugin.strafe_right()
            return f"Movement: {result}"
        elif function_name == "stop_robot":
            logger.info("Executing JSON command: stop robot")
            result = self.movement_plugin.stop_robot()
            return f"Movement: {result}"
        elif function_name == "get_movement_status":
            logger.info("Executing JSON command: get movement status")
            result = self.movement_plugin.get_movement_status()
            return f"Movement status: {result}"
        else:
            return f"Unknown function: {function_name}"
    
    def cleanup(self):
        """Clean up resources."""
        if self.led_controller:
            self.led_controller.cleanup()
        if self.movement_controller:
            self.movement_controller.cleanup()
