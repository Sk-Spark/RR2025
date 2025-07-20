#!/bin/bash

# Quick Start Guide for AI Bot Controller
# This script provides a guided setup and testing process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo -e "${NC}"
}

# Function to wait for user input
wait_for_user() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Check if we're in the right directory
check_directory() {
    if [ ! -f "main.py" ]; then
        print_error "Please run this script from the AiBot directory"
        print_info "Expected location: /home/spark/RR2025/AiBot/"
        exit 1
    fi
}

# Main script
main() {
    clear
    print_header "🤖 AI Bot Controller - Quick Start Guide"
    
    echo "This guide will help you set up and test your AI Bot Controller."
    echo "Make sure you have:"
    echo "  • Raspberry Pi 5 with Hailo AI Hat+"
    echo "  • Camera module connected"
    echo "  • Motors and servos wired according to the documentation"
    echo "  • MPU6050 sensor connected via I2C"
    echo ""
    wait_for_user
    
    # Check directory
    check_directory
    
    # Step 1: Run system tests
    print_step "1. Running system tests..."
    print_info "This will check if all components are properly installed and configured."
    wait_for_user
    
    if python3 test_system.py; then
        print_success "System tests passed!"
    else
        print_warning "Some tests failed. You can still continue, but some features may not work."
        echo "Do you want to continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Run './setup.sh' to install dependencies and try again."
            exit 1
        fi
    fi
    
    echo ""
    wait_for_user
    
    # Step 2: Check hardware connections
    print_step "2. Checking hardware connections..."
    print_info "Scanning I2C bus for connected devices..."
    
    if command -v i2cdetect &> /dev/null; then
        echo "I2C scan results:"
        i2cdetect -y 1
        echo ""
        print_info "Look for:"
        print_info "  • 0x40: PCA9685 (motor/servo controller)"
        print_info "  • 0x68: MPU6050 (IMU sensor)"
    else
        print_warning "i2cdetect not found. Install i2c-tools: sudo apt install i2c-tools"
    fi
    
    echo ""
    wait_for_user
    
    # Step 3: Test camera
    print_step "3. Testing camera..."
    print_info "Taking a test photo to verify camera functionality..."
    
    if command -v libcamera-still &> /dev/null; then
        if libcamera-still -o test_photo.jpg --timeout 2000; then
            print_success "Camera test successful! Photo saved as test_photo.jpg"
        else
            print_warning "Camera test failed. Check camera connection and enable camera interface."
        fi
    else
        print_warning "libcamera-still not found. Camera may not be properly configured."
    fi
    
    echo ""
    wait_for_user
    
    # Step 4: Start the AI Bot Controller
    print_step "4. Starting AI Bot Controller..."
    print_info "The web interface will be available at: http://$(hostname -I | cut -d' ' -f1):5000"
    print_info "You can access it from any device on your network."
    echo ""
    print_warning "Press Ctrl+C to stop the controller when you're done testing."
    echo ""
    wait_for_user
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        print_info "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Start the controller
    print_success "Starting AI Bot Controller..."
    print_info "Web interface will be available at: http://$(hostname -I | cut -d' ' -f1):5000"
    
    # Run the main application
    python main.py
}

# Help function
show_help() {
    echo "AI Bot Controller Quick Start Guide"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -t, --test     Run system tests only"
    echo "  -s, --setup    Run setup script"
    echo ""
    echo "Examples:"
    echo "  $0             Start the quick start guide"
    echo "  $0 --test      Run system tests only"
    echo "  $0 --setup     Run the setup script"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -t|--test)
        check_directory
        python3 test_system.py
        exit $?
        ;;
    -s|--setup)
        check_directory
        ./setup.sh
        exit $?
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
