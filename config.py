"""
Configuration settings for Toy ASI-ARCH
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """System configuration"""
    
    # Workspace paths
    BASE_DIR = Path.cwd()
    WORKSPACE_DIR = BASE_DIR / "research_workspace"
    EXPERIMENTS_DIR = WORKSPACE_DIR / "experiments"
    COGNITIONS_DIR = WORKSPACE_DIR / "cognitions"
    TEMP_DIR = WORKSPACE_DIR / "temp"
    
    # Model settings
    USE_LOCAL_MODEL = True  # Use Ollama for free operation
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Model selection
    if USE_LOCAL_MODEL:
        MODEL_PROVIDER = "ollama"
        MODEL_NAME = "mistral"  # or "llama2", "codellama"
        MODEL_ENDPOINT = "http://localhost:11434"
    else:
        MODEL_PROVIDER = "openai"
        MODEL_NAME = "gpt-3.5-turbo"
        
    # Resource limits
    MAX_EXECUTION_TIME = 30  # seconds per experiment
    MAX_MEMORY_MB = 1024  # MB per experiment
    MAX_OUTPUT_SIZE = 10000  # characters
    
    # Research parameters
    MAX_ITERATIONS = 100
    EXPERIMENTS_PER_ITERATION = 3
    HYPOTHESIS_TEMPERATURE = 0.7
    ANALYSIS_DEPTH = "basic"  # basic, moderate, deep
    
    # Safety settings
    SAFE_MODE = True  # Sandbox code execution
    ALLOWED_IMPORTS = [
        "math", "random", "itertools", "collections",
        "numpy", "pandas", "statistics", "time"
    ]
    
    # Performance settings
    ITERATION_DELAY = 2  # seconds between iterations
    API_RETRY_ATTEMPTS = 3
    API_RETRY_DELAY = 5  # seconds
    
    # Logging
    DEBUG_MODE = False
    LOG_LEVEL = "INFO" if not DEBUG_MODE else "DEBUG"
    
    # Experiment tracking
    KEEP_FAILED_EXPERIMENTS = True
    MAX_STORED_EXPERIMENTS = 1000
    
    # Analysis parameters
    MIN_IMPROVEMENT_THRESHOLD = 0.05  # 5% improvement to be significant
    STATISTICAL_CONFIDENCE = 0.95
    
    # Cognition base settings
    MAX_INSIGHTS_STORED = 500
    INSIGHT_RELEVANCE_THRESHOLD = 0.7
    
    # Hardware optimization
    @classmethod
    def optimize_for_hardware(cls):
        """Adjust settings based on available resources"""
        import psutil
        
        # Get system resources
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        
        # Adjust based on RAM
        if ram_gb < 8:
            cls.MAX_MEMORY_MB = 512
            cls.EXPERIMENTS_PER_ITERATION = 1
            cls.MODEL_NAME = "mistral" if cls.USE_LOCAL_MODEL else "gpt-3.5-turbo"
            print(f"Low memory detected ({ram_gb:.1f}GB). Adjusted settings.")
        elif ram_gb > 16:
            cls.MAX_MEMORY_MB = 2048
            cls.EXPERIMENTS_PER_ITERATION = 5
            print(f"High memory detected ({ram_gb:.1f}GB). Enhanced settings.")
            
        # Adjust based on CPU
        if cpu_count < 4:
            cls.MAX_EXECUTION_TIME = 60
            print(f"Low CPU count ({cpu_count}). Extended execution time.")
            
        return cls

# Auto-optimize on import
Config = Config.optimize_for_hardware()