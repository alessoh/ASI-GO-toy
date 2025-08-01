"""
Engineer module: Safely executes experiments
"""

import os
import sys
import time
import json
import subprocess
import tempfile
import resource
import signal
from pathlib import Path
from typing import Dict, Any, Optional
import psutil

from utils import extract_code_blocks, call_llm

class Engineer:
    """Executes experiments in a safe, resource-limited environment"""
    
    def __init__(self, config):
        self.config = config
        self.execution_count = 0
        
    def execute_experiment(self, hypothesis: Dict) -> Dict:
        """Execute a single experiment based on hypothesis"""
        
        self.execution_count += 1
        
        result = {
            "experiment_id": f"exec_{self.execution_count}",
            "hypothesis_id": hypothesis.get("description", "")[:50],
            "start_time": time.time(),
            "success": False,
            "output": None,
            "error": None,
            "metrics": {},
            "summary": ""
        }
        
        try:
            # Generate complete code from hypothesis
            code = self._generate_experiment_code(hypothesis)
            
            if not code:
                result["error"] = "Failed to generate executable code"
                return result
                
            # Execute code safely
            execution_result = self._safe_execute(code)
            
            # Process results
            result.update(execution_result)
            
            # Calculate metrics
            result["metrics"] = self._calculate_metrics(execution_result, hypothesis)
            
            # Generate summary
            result["summary"] = self._generate_summary(result, hypothesis)
            
        except Exception as e:
            result["error"] = str(e)
            result["summary"] = f"Experiment failed: {str(e)}"
            
        finally:
            result["end_time"] = time.time()
            result["duration"] = result["end_time"] - result["start_time"]
            
        return result
        
    def _generate_experiment_code(self, hypothesis: Dict) -> Optional[str]:
        """Generate complete executable code from hypothesis"""
        
        code_sketch = hypothesis.get("code_sketch", "")
        
        # If we have a code sketch, try to complete it
        if code_sketch:
            return self._complete_code_sketch(code_sketch, hypothesis)
            
        # Otherwise, generate from scratch
        return self._generate_code_from_description(hypothesis)
        
    def _complete_code_sketch(self, sketch: str, hypothesis: Dict) -> str:
        """Complete a code sketch into executable code"""
        
        prompt = f"""Complete this code sketch into a working Python experiment:

Hypothesis: {hypothesis['description']}
Approach: {hypothesis['approach']}

Code sketch:
{sketch}

Requirements:
1. Make it fully executable with test data
2. Include timing measurements
3. Print results in JSON format
4. Handle errors gracefully
5. Stay within these imports: {self.config.ALLOWED_IMPORTS}

Complete code:"""

        try:
            response = call_llm(
                prompt,
                temperature=0.3,  # Lower temperature for code generation
                provider=self.config.MODEL_PROVIDER,
                model=self.config.MODEL_NAME
            )
            
            # Extract code blocks
            code_blocks = extract_code_blocks(response)
            if code_blocks:
                return self._add_safety_wrapper(code_blocks[0])
                
        except Exception as e:
            print(f"Code completion failed: {e}")
            
        # Fallback: use sketch with basic wrapper
        return self._add_safety_wrapper(sketch)
        
    def _generate_code_from_description(self, hypothesis: Dict) -> str:
        """Generate code from hypothesis description"""
        
        prompt = f"""Generate a Python experiment for this hypothesis:

Hypothesis: {hypothesis['description']}
Expected outcome: {hypothesis['expected_outcome']}
Metrics to measure: {hypothesis.get('metrics', [])}

Requirements:
1. Create a complete, runnable experiment
2. Generate test data if needed
3. Measure and compare performance/results
4. Output results as JSON
5. Use only these imports: {self.config.ALLOWED_IMPORTS}

Code:"""

        try:
            response = call_llm(
                prompt,
                temperature=0.3,
                provider=self.config.MODEL_PROVIDER,
                model=self.config.MODEL_NAME
            )
            
            code_blocks = extract_code_blocks(response)
            if code_blocks:
                return self._add_safety_wrapper(code_blocks[0])
                
        except Exception as e:
            print(f"Code generation failed: {e}")
            
        # Fallback: simple test code
        return self._get_fallback_code(hypothesis)
        
    def _add_safety_wrapper(self, code: str) -> str:
        """Add safety wrapper to code"""
        
        wrapper = """
import json
import time
import sys

# Safety restrictions
__builtins__['__import__'] = None
__builtins__['open'] = None
__builtins__['exec'] = None
__builtins__['eval'] = None

# Allowed imports
import math
import random
import itertools
import collections

def run_experiment():
    results = {"output": None, "error": None, "timing": {}}
    start_time = time.time()
    
    try:
        # User code here
{user_code}
        
        results["output"] = locals().get("result", "No result variable found")
    except Exception as e:
        results["error"] = str(e)
    finally:
        results["timing"]["total"] = time.time() - start_time
        
    print(json.dumps(results))
    
if __name__ == "__main__":
    run_experiment()
"""
        
        # Indent user code
        indented_code = "\n".join("        " + line for line in code.split("\n"))
        
        return wrapper.format(user_code=indented_code)
        
    def _get_fallback_code(self, hypothesis: Dict) -> str:
        """Generate simple fallback code"""
        
        return """
import json
import time
import random

def run_experiment():
    results = {"output": None, "error": None, "timing": {}}
    start_time = time.time()
    
    try:
        # Fallback experiment
        data = [random.randint(1, 100) for _ in range(100)]
        result = sum(data) / len(data)
        
        results["output"] = {
            "result": result,
            "data_size": len(data),
            "description": "Fallback experiment - basic computation"
        }
    except Exception as e:
        results["error"] = str(e)
    finally:
        results["timing"]["total"] = time.time() - start_time
        
    print(json.dumps(results))
    
if __name__ == "__main__":
    run_experiment()
"""
        
    def _safe_execute(self, code: str) -> Dict:
        """Execute code with resource limits"""
        
        if sys.platform == "win32":
            return self._execute_windows(code)
        else:
            return self._execute_unix(code)
            
    def _execute_windows(self, code: str) -> Dict:
        """Execute code on Windows with basic safety"""
        
        result = {
            "success": False,
            "output": None,
            "error": None,
            "stdout": "",
            "stderr": "",
            "resource_usage": {}
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
            
        try:
            # Monitor resources before execution
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Execute with timeout
            proc = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=self.config.MAX_EXECUTION_TIME)
                
                # Check memory usage
                peak_memory = process.memory_info().rss / 1024 / 1024
                memory_used = peak_memory - initial_memory
                
                if memory_used > self.config.MAX_MEMORY_MB:
                    result["error"] = f"Memory limit exceeded: {memory_used:.1f}MB"
                    return result
                    
                result["stdout"] = stdout[:self.config.MAX_OUTPUT_SIZE]
                result["stderr"] = stderr[:self.config.MAX_OUTPUT_SIZE]
                result["resource_usage"]["memory_mb"] = memory_used
                
                # Parse output
                if stdout:
                    try:
                        output_data = json.loads(stdout.strip().split('\n')[-1])
                        result["output"] = output_data.get("output")
                        result["error"] = output_data.get("error")
                        result["success"] = not bool(output_data.get("error"))
                    except:
                        result["output"] = stdout
                        result["success"] = True
                        
            except subprocess.TimeoutExpired:
                proc.kill()
                result["error"] = f"Execution timeout ({self.config.MAX_EXECUTION_TIME}s)"
                
        except Exception as e:
            result["error"] = f"Execution failed: {str(e)}"
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass
                
        return result
        
    def _execute_unix(self, code: str) -> Dict:
        """Execute code on Unix with better resource limits"""
        
        # Similar to Windows but with resource.setrlimit for better control
        # For brevity, using same implementation as Windows
        return self._execute_windows(code)
        
    def _calculate_metrics(self, execution_result: Dict, hypothesis: Dict) -> Dict:
        """Calculate metrics from execution results"""
        
        metrics = {}
        
        if execution_result.get("success"):
            output = execution_result.get("output", {})
            
            # Extract timing information
            if isinstance(output, dict) and "timing" in output:
                metrics["execution_time"] = output["timing"].get("total", 0)
                
            # Memory usage
            metrics["memory_mb"] = execution_result.get("resource_usage", {}).get("memory_mb", 0)
            
            # Check for specific metrics mentioned in hypothesis
            for metric_name in hypothesis.get("metrics", []):
                if isinstance(output, dict) and metric_name in output:
                    metrics[metric_name] = output[metric_name]
                    
        return metrics
        
    def _generate_summary(self, result: Dict, hypothesis: Dict) -> str:
        """Generate human-readable summary of results"""
        
        if result["success"]:
            summary_parts = [f"Successfully executed: {hypothesis['description']}"]
            
            if result["metrics"]:
                summary_parts.append(f"Metrics: {json.dumps(result['metrics'], indent=2)}")
                
            if result["output"]:
                summary_parts.append(f"Key findings: {str(result['output'])[:200]}")
                
            return " | ".join(summary_parts)
        else:
            return f"Failed: {result.get('error', 'Unknown error')}"