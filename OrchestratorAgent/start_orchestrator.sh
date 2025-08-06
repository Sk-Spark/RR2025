#!/bin/bash

# Orchestrator Agent Startup Script
# This script starts the orchestrator with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="/home/spark/.venv"
PYTHON_CMD="${VENV_PATH}/bin/python"
LOG_DIR="${SCRIPT_DIR}/logs"

# Functions
print_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}🤖 ORCHESTRATOR AGENT STARTUP SCRIPT 🤖${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python_env() {
    print_status "Checking Python environment..."
    
    if [ ! -f "$PYTHON_CMD" ]; then
        print_error "Python virtual environment not found at $VENV_PATH"
        print_error "Please ensure the virtual environment is set up correctly"
        exit 1
    fi
    
    # Check Python version
    python_version=$($PYTHON_CMD --version 2>&1)
    print_status "Python version: $python_version"
    
    # Check if we're in the right directory
    if [ ! -f "$SCRIPT_DIR/main.py" ]; then
        print_error "main.py not found. Please run this script from the OrchestratorAgent directory"
        exit 1
    fi
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check semantic-kernel
    if ! $PYTHON_CMD -c "import semantic_kernel" 2>/dev/null; then
        print_error "semantic-kernel not installed"
        print_status "Installing dependencies..."
        $PYTHON_CMD -m pip install -r requirements.txt
    fi
    
    # Check websockets
    if ! $PYTHON_CMD -c "import websockets" 2>/dev/null; then
        print_error "websockets not installed"
        exit 1
    fi
    
    # Check ollama
    if ! $PYTHON_CMD -c "import ollama" 2>/dev/null; then
        print_warning "ollama package not found, but may not be critical"
    fi
    
    print_status "Dependencies check completed"
}

check_ollama_service() {
    print_status "Checking Ollama service..."
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_status "✅ Ollama service is running"
        
        # Check if LLaMA model is available
        if curl -s http://localhost:11434/api/tags | grep -q "llama3.2:3b"; then
            print_status "✅ LLaMA 3.2:3B model is available"
        else
            print_warning "⚠️ LLaMA 3.2:3B model not found"
            print_status "You may need to run: ollama pull llama3.2:3b"
        fi
    else
        print_warning "⚠️ Ollama service not accessible at localhost:11434"
        print_status "The orchestrator will start but LLM features may not work"
    fi
}

setup_logs() {
    print_status "Setting up log directory..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    # Set permissions
    chmod 755 "$LOG_DIR"
    
    print_status "Log directory ready: $LOG_DIR"
}

check_ports() {
    print_status "Checking required ports..."
    
    # Check if port 8080 is available
    if netstat -tuln 2>/dev/null | grep -q ":8080 "; then
        print_warning "⚠️ Port 8080 is already in use"
        print_status "You may need to change WEBSOCKET_PORT in .env"
    else
        print_status "✅ Port 8080 is available"
    fi
}

start_orchestrator() {
    print_status "Starting Orchestrator Agent..."
    print_status "Working directory: $SCRIPT_DIR"
    print_status "Python command: $PYTHON_CMD"
    
    cd "$SCRIPT_DIR"
    
    # Export environment variables
    export PYTHONPATH="$SCRIPT_DIR/src:$SCRIPT_DIR/config:$PYTHONPATH"
    
    # Start the orchestrator
    exec $PYTHON_CMD main.py
}

cleanup() {
    print_status "Cleaning up..."
    # Add any cleanup tasks here
}

# Signal handlers
trap cleanup EXIT
trap 'print_warning "Received interrupt signal"; exit 130' INT TERM

# Main execution
main() {
    print_header
    
    check_python_env
    check_dependencies
    check_ollama_service
    setup_logs
    check_ports
    
    echo
    print_status "All checks completed successfully!"
    print_status "Starting orchestrator in 3 seconds..."
    echo
    
    sleep 3
    
    start_orchestrator
}

# Handle command line arguments
case "${1:-}" in
    "check")
        print_header
        check_python_env
        check_dependencies
        check_ollama_service
        check_ports
        print_status "✅ All checks completed"
        ;;
    "logs")
        print_status "Showing recent logs..."
        if [ -f "$LOG_DIR/orchestrator.log" ]; then
            tail -f "$LOG_DIR/orchestrator.log"
        else
            print_error "No log file found at $LOG_DIR/orchestrator.log"
        fi
        ;;
    "status")
        print_status "Checking orchestrator status..."
        if pgrep -f "python.*main.py" >/dev/null; then
            print_status "✅ Orchestrator is running"
            print_status "PID: $(pgrep -f 'python.*main.py')"
        else
            print_warning "⚠️ Orchestrator is not running"
        fi
        ;;
    "stop")
        print_status "Stopping orchestrator..."
        pkill -f "python.*main.py" || print_warning "No orchestrator process found"
        print_status "✅ Stop signal sent"
        ;;
    "restart")
        print_status "Restarting orchestrator..."
        pkill -f "python.*main.py" || print_warning "No orchestrator process found"
        sleep 2
        main
        ;;
    "help"|"-h"|"--help")
        echo "Orchestrator Agent Startup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Start the orchestrator (default)"
        echo "  check      Run system checks without starting"
        echo "  logs       Show recent logs (tail -f)"
        echo "  status     Check if orchestrator is running"
        echo "  stop       Stop the orchestrator"
        echo "  restart    Restart the orchestrator"
        echo "  help       Show this help message"
        echo ""
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        print_status "Use '$0 help' for available commands"
        exit 1
        ;;
esac
