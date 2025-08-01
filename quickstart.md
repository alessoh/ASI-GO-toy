# Quick Start Guide

Get Toy ASI-ARCH running in 5 minutes!

## 1. Prerequisites

- Windows 10/11
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- 8GB+ RAM

## 2. Installation

Open Command Prompt or PowerShell and run:

```cmd
# Clone or download the project
cd C:\
mkdir ToyASIARCH
cd ToyASIARCH

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

## 3. First Run

```cmd
python main.py
```

Enter a research objective like:
- "Find efficient algorithms for sorting small arrays"
- "Optimize prime number detection"
- "Create compression algorithms for text"

## 4. Monitor Progress

- Watch the console for real-time updates
- Check `research_workspace\research_log.txt` for detailed logs
- Results saved in `research_workspace\experiments\`

## 5. Tips

- **Start simple**: Test with basic objectives first
- **Be patient**: Each experiment takes 30-60 seconds
- **Check resources**: Use Task Manager to monitor CPU/RAM
- **Use Ctrl+C**: Pause research anytime

## Troubleshooting

**"Python not found"**
- Ensure Python is in PATH
- Restart terminal after installing Python

**Memory errors**
- Close other applications
- Reduce experiments per iteration in config.py

**Slow performance**
- Normal for first run (downloading models)
- Subsequent runs will be faster

## Using Without Internet

The system can run completely offline:
1. Install Ollama: https://ollama.ai/download/windows
2. Pull a model: `ollama pull mistral`
3. Set `USE_LOCAL_MODEL = True` in config.py

## Next Steps

- Read the full README.md for detailed documentation
- Explore different research objectives
- Modify config.py for your hardware
- Check research reports in `research_workspace\`

Happy researching! 🔬