#!/bin/bash

# AiBot Setup Script
# This script creates a virtual environment and installs all required dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${BLUE}=== AiBot Setup Script ===${NC}"
echo "Project directory: $PROJECT_DIR"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+')
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
            PYTHON_CMD="python"
        else
            print_error "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+')
    print_status "Found Python $PYTHON_VERSION"
}

# Check if pip is available
check_pip() {
    print_status "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "pip is not available. Please install pip for Python 3."
        exit 1
    fi
    
    print_status "pip is available"
}

# Create virtual environment
create_venv() {
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_status "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_status "Virtual environment created successfully"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    if [ $? -ne 0 ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_status "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    if [ $? -ne 0 ]; then
        print_warning "Failed to upgrade pip, continuing anyway..."
    else
        print_status "pip upgraded successfully"
    fi
}

# Install requirements
install_requirements() {
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found in $PROJECT_DIR"
        exit 1
    fi
    
    print_status "Installing requirements from requirements.txt..."
    python -m pip install -r "$PROJECT_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install requirements"
        exit 1
    fi
    
    print_status "Requirements installed successfully"
}

# Install development dependencies (optional)
install_dev_dependencies() {
    print_status "Installing development dependencies..."
    python -m pip install pytest>=7.0.0 pytest-asyncio>=0.21.0 black>=22.0.0 flake8>=4.0.0 mypy>=1.0.0
    
    if [ $? -ne 0 ]; then
        print_warning "Failed to install development dependencies, continuing anyway..."
    else
        print_status "Development dependencies installed successfully"
    fi
}

# Install the package in development mode
install_package() {
    if [ -f "$PROJECT_DIR/setup.py" ]; then
        print_status "Installing AiBot package in development mode..."
        python -m pip install -e .
        
        if [ $? -ne 0 ]; then
            print_warning "Failed to install package in development mode, continuing anyway..."
        else
            print_status "AiBot package installed in development mode"
        fi
    else
        print_warning "setup.py not found, skipping package installation"
    fi
}

# Create activation script
create_activation_script() {
    print_status "Creating activation script..."
    cat > "$PROJECT_DIR/activate_venv.sh" << 'EOF'
#!/bin/bash
# Activation script for AiBot virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo "Activating AiBot virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo "Virtual environment activated. Use 'deactivate' to exit."
else
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi
EOF
    
    chmod +x "$PROJECT_DIR/activate_venv.sh"
    print_status "Activation script created at $PROJECT_DIR/activate_venv.sh"
}

# Main setup process
main() {
    cd "$PROJECT_DIR"
    
    check_python
    check_pip
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    
    # Ask if user wants development dependencies
    read -p "Do you want to install development dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dev_dependencies
    fi
    
    install_package
    create_activation_script
    
    echo
    print_status "Setup completed successfully!"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Activate the virtual environment:"
    echo "   source ./activate_venv.sh"
    echo "   OR"
    echo "   source venv/bin/activate"
    echo
    echo "2. Run the AiBot application:"
    echo "   python main.py"
    echo
    echo "3. To deactivate the virtual environment:"
    echo "   deactivate"
    echo
    print_status "Happy coding! 🤖"
}

# Run main function
main "$@"
