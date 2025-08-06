# Changelog

All notable changes to the AiBot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-05

### Added
- Complete project restructure with proper Python package layout
- Modular architecture with separate modules for core, hardware, plugins, agents, and communication
- 1-second auto-stop safety mechanism for all movements
- Comprehensive movement control with mecanum wheel patterns
- Natural language command processing using Ollama LLM
- Semantic Kernel plugin architecture for extensibility
- Hardware diagnostic tools and comprehensive test suite
- Proper package structure with setup.py for installation
- Documentation and project setup files

### Changed
- Reorganized codebase into proper Python package structure
- Updated import statements to use relative imports
- Improved error handling and logging throughout the system
- Enhanced movement controller with async/await patterns

### Fixed
- AsyncIO cancellation errors in movement controller
- LLM decision parsing issues with prompt templates
- Import resolution problems with new package structure
- Motor control timing and synchronization issues

### Security
- Added 1-second auto-stop safety for all movement commands
- Implemented proper error handling and graceful failure recovery

## [0.9.0] - 2025-08-04

### Added
- Movement plugin with 1-second auto-stop delays
- PCA9685 PWM controller integration
- Motor control for 4-wheel mecanum setup
- Hardware abstraction layer

### Changed
- Enhanced configuration system for movement parameters
- Updated application UI to show movement commands

### Fixed
- Motor initialization and stopping issues
- PWM signal generation and timing

## [0.8.0] - 2025-08-03

### Added
- Semantic Kernel plugin architecture
- LED control plugin system
- Modular design for easy extension

### Changed
- Refactored agent system to use plugins
- Improved code organization and modularity

## [0.7.0] - 2025-08-02

### Added
- Ollama LLM integration for natural language processing
- LED control with GPIO integration
- Basic application framework and configuration system

### Changed
- Initial project structure and organization

## [0.6.0] - 2025-08-01

### Added
- Initial project setup
- Basic LED controller implementation
- WebSocket communication framework

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
