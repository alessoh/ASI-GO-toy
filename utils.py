"""
Utility functions for Toy ASI-ARCH
"""

import os
import re
import json
import logging
import requests
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
import sys
import platform

def setup_logging(log_file: Path, level: str = "INFO") -> logging.Logger:
    """Set up logging configuration"""
    
    # Create logger
    logger = logging.getLogger("ToyASIARCH")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Simple formatter for console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def ensure_directories(directories: List[Path]):
    """Ensure all directories exist"""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def display_banner():
    """Display startup banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║      TOY ASI-ARCH v1.0               ║
    ║   Autonomous Research System          ║
    ║   For Windows Laptops                 ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)

def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from text"""
    
    # Pattern for ```python or ``` code blocks
    pattern = r'```(?:python)?\n(.*?)\n```'
    
    matches = re.findall(pattern, text, re.DOTALL)
    
    # If no triple-backtick blocks, try to find indented code
    if not matches:
        # Look for lines that start with 4 spaces or a tab
        lines = text.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                in_code_block = True
                code_lines.append(line[4:] if line.startswith('    ') else line[1:])
            elif in_code_block and line.strip() == '':
                code_lines.append('')
            elif in_code_block:
                # End of code block
                if code_lines:
                    matches.append('\n'.join(code_lines))
                code_lines = []
                in_code_block = False
                
        # Add any remaining code
        if code_lines:
            matches.append('\n'.join(code_lines))
            
    return matches

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity (0-1)"""
    
    if not text1 or not text2:
        return 0.0
        
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
        
    # Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def call_llm(prompt: str, temperature: float = 0.7, 
             provider: str = "ollama", model: str = "mistral") -> str:
    """Call LLM with fallback options"""
    
    if provider == "ollama":
        return call_ollama(prompt, model, temperature)
    elif provider == "openai":
        return call_openai(prompt, model, temperature)
    else:
        # Fallback to simple response
        return generate_fallback_response(prompt)

def call_ollama(prompt: str, model: str = "mistral", temperature: float = 0.7) -> str:
    """Call Ollama API"""
    
    # First, ensure Ollama is installed and running
    if not is_ollama_available():
        print("Ollama not found. Installing...")
        install_ollama()
        
    # Check if model is available
    ensure_ollama_model(model)
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"Ollama error: {response.status_code}")
            return generate_fallback_response(prompt)
            
    except requests.exceptions.ConnectionError:
        print("Ollama not running. Starting...")
        start_ollama()
        time.sleep(5)  # Give it time to start
        
        # Retry once
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "")
        except:
            pass
            
    except Exception as e:
        print(f"Ollama error: {e}")
        
    return generate_fallback_response(prompt)

def call_openai(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
    """Call OpenAI API"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("OpenAI API key not found. Using fallback.")
        return generate_fallback_response(prompt)
        
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI error: {response.status_code}")
            return generate_fallback_response(prompt)
            
    except Exception as e:
        print(f"OpenAI error: {e}")
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt: str) -> str:
    """Generate simple fallback response without LLM"""
    
    prompt_lower = prompt.lower()
    
    # Simple pattern-based responses
    if "hypothesis" in prompt_lower:
        return """HYPOTHESIS: Test algorithmic improvement
APPROACH: Iterative optimization
CODE_SKETCH:
```python
def improved_algorithm(data):
    # Process data efficiently
    result = []
    for item in data:
        result.append(process(item))
    return result
```
EXPECTED_OUTCOME: Improved performance
METRICS: execution_time, accuracy"""
    
    elif "analyze" in prompt_lower:
        return json.dumps({
            "key_findings": ["Algorithm executed successfully"],
            "patterns": ["Linear time complexity observed"],
            "recommendations": ["Test with larger datasets"]
        })
        
    elif "complete" in prompt_lower and "code" in prompt_lower:
        return """```python
import time
import json

def run_experiment():
    start_time = time.time()
    
    # Sample experiment
    data = list(range(100))
    result = sum(data)
    
    end_time = time.time()
    
    output = {
        "result": result,
        "execution_time": end_time - start_time
    }
    
    print(json.dumps({"output": output, "error": None}))

if __name__ == "__main__":
    run_experiment()
```"""
    
    else:
        return "Fallback response: Please ensure LLM is properly configured."

def is_ollama_available() -> bool:
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def install_ollama():
    """Install Ollama for Windows"""
    
    print("Installing Ollama...")
    
    if platform.system() == "Windows":
        # Download installer
        installer_url = "https://ollama.ai/download/windows"
        print(f"Please download and install Ollama from: {installer_url}")
        print("After installation, restart this program.")
        input("Press Enter when installation is complete...")
    else:
        print("Please install Ollama for your platform from: https://ollama.ai/download")
        
def start_ollama():
    """Start Ollama service"""
    
    if platform.system() == "Windows":
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print("Started Ollama service")
        except:
            print("Could not start Ollama. Please start it manually.")
    else:
        try:
            subprocess.Popen(["ollama", "serve"])
        except:
            print("Could not start Ollama. Please start it manually.")

def ensure_ollama_model(model: str):
    """Ensure Ollama model is available"""
    
    try:
        # Check if model exists
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        
        if model not in result.stdout:
            print(f"Downloading {model} model... This may take a few minutes.")
            subprocess.run(["ollama", "pull", model])
            
    except Exception as e:
        print(f"Error checking Ollama model: {e}")

def format_time(seconds: float) -> str:
    """Format time duration in human-readable format"""
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string with ellipsis"""
    
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."

def clean_json_output(text: str) -> Dict:
    """Extract JSON from potentially messy output"""
    
    # Try to find JSON in the text
    json_pattern = r'\{[^{}]*\}'
    
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in reversed(matches):  # Try from end first
        try:
            return json.loads(match)
        except:
            continue
            
    # If no valid JSON found, return empty dict
    return {}