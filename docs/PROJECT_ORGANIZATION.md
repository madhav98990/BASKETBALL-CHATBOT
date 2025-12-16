# Project Organization

This document describes the organized structure of the Basketball Chatbot project.

## Directory Structure

### Root Level Files
- `chatbot.py` - Main chatbot entry point
- `config.py` - Configuration file
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker configuration
- `README.md` - Main project documentation
- `env_template.txt` - Environment variable template

### Core Directories

#### `agents/`
Contains all agent modules that handle different types of queries:
- Intent detection
- Stats retrieval
- Player statistics
- Schedule queries
- Article search
- Response formatting
- And more...

#### `services/`
External API service integrations:
- NBA API services
- ESPN API
- Ball Don't Lie API
- Other third-party services

#### `database/`
Database-related files:
- Schema definitions
- Seed data
- Database connection utilities
- Migration scripts

#### `api/`
FastAPI server implementation:
- Main API endpoint
- Request/response handling

#### `frontend/`
Web frontend files:
- HTML interface
- JavaScript client

### Utility Directories

#### `scripts/`
Organized utility scripts:
- **`debug/`** - Debug and troubleshooting scripts
  - `debug_*.py` - Debug scripts
  - `check_*.py` - Verification scripts
  - `verify_*.py` - Validation scripts
  - `final_*.py` - Final test scripts

- **`setup/`** - Setup and installation scripts
  - `setup_*.py` - Setup scripts
  - `setup_*.bat` / `setup_*.sh` - Platform-specific setup
  - `install_*.bat` - Installation scripts
  - `run.bat` / `run.sh` - Run scripts
  - `start_*.bat` / `start_*.ps1` - Start scripts

- **`quick_tests/`** - Quick test scripts
  - `quick_*.py` - Quick test scripts
  - `simple_test.py` - Simple tests
  - `demo_*.py` - Demo scripts

#### `test/`
Comprehensive test suite:
- Unit tests
- Integration tests
- End-to-end tests

#### `validate/`
Validation scripts:
- Query validation
- Data validation
- Team validation

#### `tools/`
Utility tools:
- Helper scripts
- Standalone tools

#### `docs/`
Documentation files:
- Implementation guides
- Setup instructions
- API documentation
- Troubleshooting guides

#### `data/`
Data files:
- `articles/` - Scraped article files

#### `logs/`
Log files:
- Application logs
- Installation logs

## File Organization Principles

1. **Main application code** stays at root or in core directories (`agents/`, `services/`, etc.)
2. **Scripts** are organized by purpose in `scripts/` subdirectories
3. **Documentation** is centralized in `docs/`
4. **Tests** are in the `test/` directory
5. **Data files** are in `data/`
6. **Logs** are in `logs/`

## Import Paths

All imports should use relative paths from the project root:
- `from agents.intent_detection_agent import IntentDetectionAgent`
- `from services.nba_api import NBAApiService`
- `from database.db_connection import db`

Scripts in subdirectories may need to adjust their import paths:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## Running Scripts

### Setup Scripts
```bash
# Windows
scripts\setup\setup_docker.bat
scripts\setup\start_server.bat

# Linux/Mac
./scripts/setup/setup_docker.sh
./scripts/setup/start_server.sh
```

### Debug Scripts
```bash
python scripts/debug/debug_nba_api.py
python scripts/debug/check_environment.py
```

### Quick Tests
```bash
python scripts/quick_tests/quick_test_api.py
python scripts/quick_tests/simple_test.py
```

## Maintenance

When adding new files:
1. Place them in the appropriate directory based on their purpose
2. Update this document if creating new directories
3. Follow the existing naming conventions
4. Add `__init__.py` files for Python packages

