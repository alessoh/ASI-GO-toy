"""
Researcher module: Generates hypotheses for experiments
"""

import json
import random
from typing import List, Dict, Any
from datetime import datetime

from utils import call_llm, extract_code_blocks

class Researcher:
    """Generates research hypotheses based on objectives and past results"""
    
    def __init__(self, config, cognition_base):
        self.config = config
        self.cognition_base = cognition_base
        self.hypothesis_templates = self._load_templates()
        
    def _load_templates(self):
        """Load hypothesis generation templates"""
        return {
            "optimization": [
                "What if we modify {algorithm} by {modification} to improve {metric}?",
                "Can we combine {approach1} with {approach2} to achieve better {outcome}?",
                "Would {technique} reduce the complexity of {process}?"
            ],
            "discovery": [
                "Is there a pattern in {data} that correlates with {property}?",
                "Can we find a {relationship} between {variable1} and {variable2}?",
                "What emerges when we apply {method} to {problem}?"
            ],
            "algorithm": [
                "Can we design an algorithm that {goal} in O({complexity}) time?",
                "What if we use {datastructure} to solve {problem} more efficiently?",
                "Is there a {approach} solution to {challenge}?"
            ]
        }
        
    def generate_hypotheses(self, objective: str, recent_experiments: List[Dict]) -> List[Dict]:
        """Generate hypotheses for the current iteration"""
        
        # Get relevant insights from cognition base
        insights = self.cognition_base.get_relevant_insights(objective, limit=5)
        
        # Analyze recent experiments for patterns
        patterns = self._analyze_recent_patterns(recent_experiments)
        
        # Generate diverse hypotheses
        hypotheses = []
        
        # 1. LLM-based hypothesis generation
        llm_hypotheses = self._generate_llm_hypotheses(objective, insights, patterns)
        hypotheses.extend(llm_hypotheses)
        
        # 2. Template-based variations
        template_hypotheses = self._generate_template_hypotheses(objective, patterns)
        hypotheses.extend(template_hypotheses)
        
        # 3. Mutation-based hypotheses (if we have past successes)
        if recent_experiments:
            mutation_hypotheses = self._generate_mutations(recent_experiments)
            hypotheses.extend(mutation_hypotheses)
        
        # Score and rank hypotheses
        scored_hypotheses = self._score_hypotheses(hypotheses, recent_experiments)
        
        # Return top hypotheses
        return scored_hypotheses[:self.config.EXPERIMENTS_PER_ITERATION * 2]
        
    def _analyze_recent_patterns(self, experiments: List[Dict]) -> Dict:
        """Extract patterns from recent experiments"""
        patterns = {
            "successful_approaches": [],
            "failed_approaches": [],
            "common_errors": [],
            "performance_trends": {}
        }
        
        for exp in experiments:
            result = exp.get("result", {})
            analysis = exp.get("analysis", {})
            
            if result.get("success", False):
                patterns["successful_approaches"].append(
                    exp["hypothesis"].get("approach", "unknown")
                )
            else:
                patterns["failed_approaches"].append(
                    exp["hypothesis"].get("approach", "unknown")
                )
                
            if result.get("error"):
                patterns["common_errors"].append(result["error"])
                
        return patterns
        
    def _generate_llm_hypotheses(self, objective: str, insights: List[Dict], 
                                patterns: Dict) -> List[Dict]:
        """Generate hypotheses using LLM"""
        
        prompt = f"""Research Objective: {objective}

Recent Insights:
{json.dumps(insights, indent=2)}

Recent Patterns:
- Successful approaches: {patterns.get('successful_approaches', [])}
- Failed approaches: {patterns.get('failed_approaches', [])}

Generate 3 specific, testable hypotheses for experiments. Each hypothesis should:
1. Be directly related to the research objective
2. Be implementable in Python code
3. Have measurable outcomes
4. Build on insights or avoid past failures

Format each hypothesis as:
HYPOTHESIS: [Brief description]
APPROACH: [Technical approach]
CODE_SKETCH:
```python
[Brief code outline]
```
EXPECTED_OUTCOME: [What we expect to observe]
METRICS: [How to measure success]
---"""

        try:
            response = call_llm(
                prompt, 
                temperature=self.config.HYPOTHESIS_TEMPERATURE,
                provider=self.config.MODEL_PROVIDER,
                model=self.config.MODEL_NAME
            )
            
            # Parse response into hypotheses
            hypotheses = self._parse_llm_response(response)
            return hypotheses
            
        except Exception as e:
            print(f"LLM hypothesis generation failed: {e}")
            return []
            
    def _parse_llm_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured hypotheses"""
        hypotheses = []
        
        # Split by hypothesis separator
        hypothesis_texts = response.split("---")
        
        for text in hypothesis_texts:
            if "HYPOTHESIS:" not in text:
                continue
                
            hypothesis = {
                "timestamp": datetime.now().isoformat(),
                "source": "llm",
                "description": "",
                "approach": "",
                "code_sketch": "",
                "expected_outcome": "",
                "metrics": []
            }
            
            # Extract fields
            lines = text.strip().split("\n")
            current_field = None
            
            for line in lines:
                if line.startswith("HYPOTHESIS:"):
                    hypothesis["description"] = line.replace("HYPOTHESIS:", "").strip()
                elif line.startswith("APPROACH:"):
                    hypothesis["approach"] = line.replace("APPROACH:", "").strip()
                elif line.startswith("EXPECTED_OUTCOME:"):
                    hypothesis["expected_outcome"] = line.replace("EXPECTED_OUTCOME:", "").strip()
                elif line.startswith("METRICS:"):
                    hypothesis["metrics"] = line.replace("METRICS:", "").strip().split(",")
                    
            # Extract code blocks
            code_blocks = extract_code_blocks(text)
            if code_blocks:
                hypothesis["code_sketch"] = code_blocks[0]
                
            if hypothesis["description"]:
                hypotheses.append(hypothesis)
                
        return hypotheses
        
    def _generate_template_hypotheses(self, objective: str, patterns: Dict) -> List[Dict]:
        """Generate hypotheses using templates"""
        hypotheses = []
        
        # Determine objective type
        obj_type = self._classify_objective(objective)
        templates = self.hypothesis_templates.get(obj_type, self.hypothesis_templates["algorithm"])
        
        # Generate variations
        for template in random.sample(templates, min(2, len(templates))):
            hypothesis = {
                "timestamp": datetime.now().isoformat(),
                "source": "template",
                "description": self._fill_template(template, objective),
                "approach": f"Template-based approach for {obj_type}",
                "code_sketch": self._generate_code_sketch(obj_type, objective),
                "expected_outcome": "Improved performance or new insights",
                "metrics": ["execution_time", "accuracy", "complexity"]
            }
            hypotheses.append(hypothesis)
            
        return hypotheses
        
    def _classify_objective(self, objective: str) -> str:
        """Classify research objective type"""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["optimize", "improve", "efficient"]):
            return "optimization"
        elif any(word in objective_lower for word in ["find", "discover", "pattern"]):
            return "discovery"
        else:
            return "algorithm"
            
    def _fill_template(self, template: str, objective: str) -> str:
        """Fill template with relevant terms from objective"""
        # Simple keyword extraction
        keywords = [w for w in objective.split() if len(w) > 4]
        
        # Basic filling (in real system, would be more sophisticated)
        filled = template
        placeholders = {
            "{algorithm}": random.choice(["algorithm", "method", "approach"]),
            "{modification}": random.choice(["parallelization", "caching", "optimization"]),
            "{metric}": random.choice(["speed", "accuracy", "memory usage"]),
            "{approach1}": random.choice(["iterative", "recursive", "dynamic"]),
            "{approach2}": random.choice(["greedy", "divide-conquer", "memoization"]),
            "{outcome}": random.choice(["performance", "results", "efficiency"])
        }
        
        for placeholder, value in placeholders.items():
            if placeholder in filled:
                filled = filled.replace(placeholder, value)
                
        return filled
        
    def _generate_code_sketch(self, obj_type: str, objective: str) -> str:
        """Generate a basic code sketch"""
        sketches = {
            "optimization": """
def optimized_solution(data):
    # TODO: Implement optimized approach
    result = []
    for item in data:
        # Process efficiently
        result.append(process(item))
    return result
""",
            "discovery": """
def find_pattern(data):
    patterns = {}
    for i, item in enumerate(data):
        # Look for patterns
        key = extract_feature(item)
        patterns[key] = patterns.get(key, 0) + 1
    return patterns
""",
            "algorithm": """
def new_algorithm(input_data):
    # Initialize
    state = initialize_state(input_data)
    
    # Main logic
    while not is_complete(state):
        state = update_state(state)
    
    return extract_result(state)
"""
        }
        
        return sketches.get(obj_type, sketches["algorithm"])
        
    def _generate_mutations(self, recent_experiments: List[Dict]) -> List[Dict]:
        """Generate mutations of successful experiments"""
        hypotheses = []
        
        # Find successful experiments
        successful = [exp for exp in recent_experiments 
                     if exp.get("result", {}).get("success", False)]
        
        if not successful:
            return hypotheses
            
        # Pick a successful experiment to mutate
        base_exp = random.choice(successful)
        base_hypothesis = base_exp["hypothesis"]
        
        # Generate mutations
        mutations = [
            {
                "type": "parameter_change",
                "description": f"Modify parameters in {base_hypothesis['description']}"
            },
            {
                "type": "combination",
                "description": f"Combine {base_hypothesis['description']} with new approach"
            },
            {
                "type": "extension",
                "description": f"Extend {base_hypothesis['description']} to handle edge cases"
            }
        ]
        
        for mutation in mutations[:1]:  # Just one mutation per iteration
            hypothesis = {
                "timestamp": datetime.now().isoformat(),
                "source": "mutation",
                "description": mutation["description"],
                "approach": f"{mutation['type']} of {base_hypothesis.get('approach', 'previous approach')}",
                "code_sketch": self._mutate_code(base_hypothesis.get("code_sketch", "")),
                "expected_outcome": "Improved upon previous success",
                "metrics": base_hypothesis.get("metrics", ["performance"])
            }
            hypotheses.append(hypothesis)
            
        return hypotheses
        
    def _mutate_code(self, original_code: str) -> str:
        """Create a mutation of existing code"""
        if not original_code:
            return "# Mutation of previous successful approach"
            
        # Simple mutation: add comment about changes
        return f"""# Mutated version
{original_code}
# TODO: Apply mutations here"""
        
    def _score_hypotheses(self, hypotheses: List[Dict], recent_experiments: List[Dict]) -> List[Dict]:
        """Score and rank hypotheses"""
        
        failed_approaches = set()
        for exp in recent_experiments:
            if not exp.get("result", {}).get("success", False):
                failed_approaches.add(exp["hypothesis"].get("approach", ""))
        
        for hypothesis in hypotheses:
            score = 1.0
            
            # Prefer novel approaches
            if hypothesis["approach"] in failed_approaches:
                score *= 0.5
                
            # Prefer LLM-generated hypotheses
            if hypothesis["source"] == "llm":
                score *= 1.2
                
            # Prefer hypotheses with clear metrics
            if len(hypothesis.get("metrics", [])) > 2:
                score *= 1.1
                
            hypothesis["score"] = score
            
        # Sort by score
        hypotheses.sort(key=lambda h: h.get("score", 0), reverse=True)
        
        return hypotheses