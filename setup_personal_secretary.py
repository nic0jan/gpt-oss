#!/usr/bin/env python3
"""
Personal Secretary Setup Script
Installs and configures the GPT-OSS Personal Secretary
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 12:
        print(f"❌ Python 3.12+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        "streamlit",
        "streamlit-chat",
        "pandas",
        "plotly",
        "sqlite3",  # Built-in with Python
        "asyncio",  # Built-in with Python
        "datetime",  # Built-in with Python
        "pathlib",  # Built-in with Python
        "logging",  # Built-in with Python
        "json",  # Built-in with Python
        "typing",  # Built-in with Python
        "dataclasses",  # Built-in with Python
        "enum",  # Built-in with Python
    ]
    
    # Install external dependencies
    external_deps = ["streamlit", "streamlit-chat", "pandas", "plotly"]
    
    for dep in external_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """streamlit>=1.28.0
streamlit-chat>=0.1.1
pandas>=2.0.0
plotly>=5.15.0
openai-harmony>=0.1.0
docker>=7.1.0
fastapi>=0.116.1
uvicorn>=0.35.0
aiohttp>=3.12.14
requests>=2.31.0
pydantic>=2.11.7
structlog>=25.4.0
tenacity>=9.1.2
html2text>=2025.4.15
lxml>=4.9.4
chz>=0.3.0
termcolor
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")

def create_startup_script():
    """Create startup script for the personal secretary"""
    startup_script = """#!/bin/bash
# Personal Secretary Startup Script

echo "🤖 Starting GPT-OSS Personal Secretary..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Start the application
echo "🚀 Starting Personal Secretary..."
streamlit run personal_secretary_ui.py --server.port 8501 --server.address 0.0.0.0
"""
    
    with open("start_personal_secretary.sh", "w") as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod("start_personal_secretary.sh", 0o755)
    print("✅ Created startup script")

def create_config_file():
    """Create configuration file"""
    config = """# Personal Secretary Configuration

[DATABASE]
# Database file path
db_path = "data/personal_secretary.db"

[GPT_OSS]
# GPT-OSS model configuration
model_name = "gpt-oss-20b"  # or "gpt-oss-120b"
reasoning_effort = "medium"  # low, medium, high
max_context_length = 8192

[TOOLS]
# Enable/disable tools
enable_python_tool = true
enable_browser_tool = false
enable_apply_patch_tool = false

[BROWSER]
# Browser tool configuration (if enabled)
exa_api_key = ""  # Set your Exa API key here
browser_timeout = 30

[UI]
# Streamlit UI configuration
page_title = "GPT-OSS Personal Secretary"
page_icon = "🤖"
layout = "wide"
theme = "light"

[NOTIFICATIONS]
# Notification settings
enable_notifications = true
notification_sound = true
reminder_minutes = [15, 60, 1440]  # 15 min, 1 hour, 1 day before
"""
    
    with open("config.ini", "w") as f:
        f.write(config)
    
    print("✅ Created configuration file")

def create_documentation():
    """Create basic documentation"""
    docs = """# GPT-OSS Personal Secretary

## Overview
Your intelligent personal secretary powered by GPT-OSS for comprehensive life management.

## Features
- 📝 Task Management
- 📁 Project Planning
- 📅 Schedule Management
- 📊 Productivity Analytics
- 💬 Intelligent Chat Assistant

## Quick Start

### 1. Setup
```bash
# Run the setup script
python3 setup_personal_secretary.py

# Or manually install dependencies
pip install -r requirements.txt
```

### 2. Start the Application
```bash
# Using the startup script
./start_personal_secretary.sh

# Or directly with Streamlit
streamlit run personal_secretary_ui.py
```

### 3. Access the Interface
Open your browser and go to: http://localhost:8501

## Usage Examples

### Creating Tasks
- Use the sidebar "Quick Add Task" form
- Or chat with the assistant: "Create a task: Review quarterly reports, high priority, due tomorrow"

### Managing Projects
- Navigate to the Projects page
- Create new projects with milestones
- Track progress and deadlines

### Getting Insights
- Check the Dashboard for daily overview
- Use Analytics page for productivity insights
- Chat with the assistant for personalized advice

## Configuration
Edit `config.ini` to customize:
- Database location
- GPT-OSS model settings
- Tool preferences
- UI appearance

## Data Storage
All data is stored in SQLite database:
- Tasks and projects: `data/personal_secretary.db`
- Configuration: `config.ini`

## Troubleshooting

### Common Issues
1. **Port already in use**: Change port in startup script
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Database errors**: Delete `data/personal_secretary.db` to reset

### Support
For issues and feature requests, please check the documentation or contact support.
"""
    
    with open("README.md", "w") as f:
        f.write(docs)
    
    print("✅ Created documentation")

def main():
    """Main setup function"""
    print("🤖 GPT-OSS Personal Secretary Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    print("✅ Created data directory")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create configuration files
    create_requirements_file()
    create_config_file()
    create_startup_script()
    create_documentation()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: ./start_personal_secretary.sh")
    print("2. Open: http://localhost:8501")
    print("3. Start managing your life with AI!")
    
    print("\n💡 Tips:")
    print("- Edit config.ini to customize settings")
    print("- Use the chat interface for natural language commands")
    print("- Check the Analytics page for productivity insights")

if __name__ == "__main__":
    main()