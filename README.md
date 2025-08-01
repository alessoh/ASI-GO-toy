# ASI-GO-toy
# Toy ASI-ARCH: Autonomous Research System for Windows

A lightweight implementation of an autonomous research system inspired by ASI-ARCH, designed to run on Windows laptops with limited resources.

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Extending the System](#extending-the-system)

## Overview

Toy ASI-ARCH is a simplified autonomous research system that:
- Accepts user-defined research objectives
- Generates hypotheses and experiments
- Executes code safely in isolated environments
- Analyzes results and learns from outcomes
- Maintains knowledge across research sessions

### Key Features
- **Flexible Research Goals**: Define any computational research objective
- **Local Operation**: Runs entirely on your laptop without cloud dependencies
- **Resource-Aware**: Designed for consumer hardware limitations
- **Transparent Process**: All operations are logged and inspectable
- **Extensible Design**: Easy to modify for specific domains

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB free space
- **Python**: 3.8 or higher

### Recommended Requirements
- **CPU**: 6+ cores
- **RAM**: 16GB
- **Storage**: 100GB free space
- **GPU**: Optional (for faster local LLM inference)

## Installation Guide

### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, **CHECK** "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Create Project Directory

```cmd
mkdir C:\ToyASIARCH
cd C:\ToyASIARCH
```

### Step 3: Set Up Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 5: Configure API Keys (Optional)

For OpenAI API usage:
1. Create a `.env` file in the project root
2. Add your API key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

For local models (recommended for cost-free operation):
1. The system will automatically download and use Ollama
2. No API keys required!

### Step 6: Initialize the System

```cmd
python setup.py
```

This will:
- Create necessary directories
- Download initial knowledge resources
- Set up configuration files
- Run system checks

## Quick Start

### Basic Usage

1. **Start the system**:
   ```cmd
   python main.py
   ```

2. **Input your research objective** when prompted:
   ```
   Enter research objective: Find efficient algorithms for detecting prime numbers
   ```

3. **Monitor progress**:
   - Check `research_workspace/research_log.txt` for real-time updates
   - View results in `research_workspace/experiments/`

### Example Research Objectives

- "Optimize bubble sort for nearly sorted arrays"
- "Find patterns in Fibonacci sequence variations"
- "Develop heuristics for solving 8-puzzle problems"
- "Create efficient data structures for sparse matrices"

## Architecture

### System Components

```
ToyASIARCH/
├── main.py                 # Entry point and orchestrator
├── researcher.py           # Hypothesis generation
├── engineer.py            # Experiment execution
├── analyst.py             # Results analysis
├── cognition_base.py      # Knowledge management
├── utils.py              # Helper functions
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── setup.py             # Installation script
└── research_workspace/   # Working directory
    ├── cognitions/      # Knowledge storage
    ├── experiments/     # Experiment records
    ├── current_state.json
    └── research_log.txt
```

### Component Interactions

1. **Cognition Base**: Stores and retrieves knowledge
2. **Researcher**: Generates hypotheses based on objectives and past results
3. **Engineer**: Safely executes experiments
4. **Analyst**: Evaluates results and extracts insights

### Information Flow

```
User Input → Researcher → Engineer → Analyst → Cognition Base
     ↑                                               ↓
     └───────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Algorithm Optimization

```python
# Research objective: "Optimize insertion sort for small datasets"

# The system will:
# 1. Generate variations of insertion sort
# 2. Test on different data patterns
# 3. Identify optimal modifications
# 4. Report performance improvements
```

### Example 2: Pattern Discovery

```python
# Research objective: "Find mathematical patterns in prime gaps"

# The system will:
# 1. Generate prime numbers
# 2. Analyze gap distributions
# 3. Propose pattern hypotheses
# 4. Validate findings
```

## Configuration

### config.py Settings

```python
# Model Settings
USE_LOCAL_MODEL = True  # Use Ollama instead of OpenAI
MODEL_NAME = "mistral"  # For local models

# Resource Limits
MAX_EXECUTION_TIME = 30  # seconds per experiment
MAX_MEMORY_MB = 1024    # MB per experiment
MAX_ITERATIONS = 100    # Total research iterations

# Research Parameters
EXPERIMENTS_PER_ITERATION = 3
HYPOTHESIS_TEMPERATURE = 0.7
ANALYSIS_DEPTH = "basic"  # basic, moderate, deep
```

### Adjusting for Your Hardware

**Low-end laptop (8GB RAM)**:
```python
MAX_MEMORY_MB = 512
EXPERIMENTS_PER_ITERATION = 1
USE_LOCAL_MODEL = True
```

**High-end laptop (32GB RAM)**:
```python
MAX_MEMORY_MB = 4096
EXPERIMENTS_PER_ITERATION = 5
ANALYSIS_DEPTH = "deep"
```

## Troubleshooting

### Common Issues

**1. "Python not found" error**
- Ensure Python is in PATH
- Restart command prompt after Python installation

**2. Memory errors**
- Reduce MAX_MEMORY_MB in config.py
- Close other applications
- Use fewer experiments per iteration

**3. Slow performance**
- Enable USE_LOCAL_MODEL for faster inference
- Reduce EXPERIMENTS_PER_ITERATION
- Simplify research objectives

**4. API rate limits**
- Switch to local models
- Add delays between API calls
- Use API key rotation

### Debug Mode

Enable detailed logging:
```python
# In config.py
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"
```

## Extending the System

### Adding Custom Domains

1. Create a domain module in `domains/`:
   ```python
   # domains/math_puzzles.py
   class MathPuzzleDomain:
       def generate_experiment(self, hypothesis):
           # Domain-specific logic
           pass
   ```

2. Register in `config.py`:
   ```python
   CUSTOM_DOMAINS = {
       "math_puzzles": MathPuzzleDomain
   }
   ```

### Custom Evaluation Metrics

Add to `analyst.py`:
```python
def custom_metric(results):
    # Your metric logic
    return score
```

### Integration with External Tools

- Jupyter notebooks: Export experiments as .ipynb
- Visualization: Auto-generate plots with matplotlib
- Version control: Git integration for experiment tracking

## Performance Tips

1. **Use local models** for cost-free operation
2. **Start with simple objectives** to test the system
3. **Monitor resource usage** with Task Manager
4. **Clear old experiments** periodically
5. **Use checkpointing** for long research sessions

## Safety and Ethics

- All code execution is sandboxed
- Resource limits prevent system overload
- No network access during experiments
- Results are logged for reproducibility

## Contributing

Feel free to extend and improve the system! Key areas:
- Additional safety measures
- More sophisticated analysis
- Better hypothesis generation
- Domain-specific modules

## License

MIT License - Free for educational and research use.

## Acknowledgments

Inspired by the ASI-ARCH paper "AlphaGo Moment for Model Architecture Discovery".