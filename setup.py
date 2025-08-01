#!/usr/bin/env python3
"""
Setup script for Toy ASI-ARCH
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor} detected")
    return True

def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment active")
        return True
    else:
        print("⚠ Warning: Not running in virtual environment")
        print("  Recommended: python -m venv venv && venv\\Scripts\\activate")
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'

def install_requirements():
    """Install required packages"""
    print("\nInstalling requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False

def create_workspace():
    """Create workspace directory structure"""
    print("\nCreating workspace...")
    
    directories = [
        "research_workspace",
        "research_workspace/experiments",
        "research_workspace/cognitions",
        "research_workspace/temp"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    print("✓ Workspace created")
    
    # Create initial files
    create_initial_files()

def create_initial_files():
    """Create initial configuration and knowledge files"""
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# OpenAI API Key (optional - for OpenAI model usage)\n")
            f.write("# OPENAI_API_KEY=your-key-here\n")
        print("✓ Created .env file")
    
    # Create initial knowledge files
    knowledge_dir = Path("research_workspace/cognitions")
    
    initial_insights = []
    insights_file = knowledge_dir / "insights.json"
    if not insights_file.exists():
        import json
        with open(insights_file, 'w') as f:
            json.dump(initial_insights, f, indent=2)
        print("✓ Created initial knowledge files")

def check_ollama():
    """Check if Ollama is available"""
    print("\nChecking Ollama installation...")
    
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Ollama is installed")
            
            # Check if a model is available
            list_result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            
            if "mistral" in list_result.stdout or "llama" in list_result.stdout:
                print("✓ Ollama models available")
            else:
                print("  Downloading mistral model...")
                print("  This will take a few minutes on first run...")
                subprocess.run(["ollama", "pull", "mistral"])
                
            return True
            
    except FileNotFoundError:
        print("⚠ Ollama not found")
        print("\nOllama enables free local LLM usage.")
        print("To install:")
        
        if platform.system() == "Windows":
            print("  1. Visit: https://ollama.ai/download/windows")
            print("  2. Download and run the installer")
            print("  3. Restart this setup script")
        else:
            print("  Visit: https://ollama.ai/download")
            
        response = input("\nContinue without Ollama? (y/n): ")
        return response.lower() == 'y'
        
    return False

def run_system_check():
    """Run system compatibility check"""
    print("\nRunning system check...")
    
    # Check RAM
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        
        print(f"✓ System resources: {ram_gb:.1f}GB RAM, {cpu_count} CPU cores")
        
        if ram_gb < 8:
            print("  ⚠ Warning: Low RAM detected. Performance may be limited.")
        
    except ImportError:
        print("  ⚠ Could not check system resources")
        
    return True

def display_next_steps():
    """Display next steps for user"""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Run the system:")
    print("   python main.py")
    print("\n2. Enter a research objective when prompted")
    print("\n3. Monitor progress in research_workspace/research_log.txt")
    
    print("\nExample objectives:")
    print("- Find efficient algorithms for detecting prime numbers")
    print("- Optimize bubble sort for nearly sorted arrays")
    print("- Develop compression algorithms for text data")
    
    print("\nTips:")
    print("- Start with simple objectives to test the system")
    print("- Check the README.md for detailed documentation")
    print("- Use Ctrl+C to pause research at any time")
    
def main():
    """Main setup routine"""
    print("TOY ASI-ARCH SETUP")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
        
    # Check virtual environment
    if not check_virtual_env():
        sys.exit(1)
        
    # Install requirements
    if not install_requirements():
        sys.exit(1)
        
    # Create workspace
    create_workspace()
    
    # Check Ollama
    check_ollama()
    
    # Run system check
    run_system_check()
    
    # Display next steps
    display_next_steps()
    
    print("\n✓ Setup completed successfully!")

if __name__ == "__main__":
    main()