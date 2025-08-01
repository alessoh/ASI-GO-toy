"""
Analyst module: Analyzes experimental results and extracts insights
"""

import json
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime

from utils import call_llm

class Analyst:
    """Analyzes experimental results and generates insights"""
    
    def __init__(self, config, cognition_base):
        self.config = config
        self.cognition_base = cognition_base
        
    def analyze_result(self, result: Dict, hypothesis: Dict, 
                      recent_experiments: List[Dict]) -> Dict:
        """Analyze a single experimental result"""
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "score": 0.0,
            "insights": {},
            "comparison": {},
            "recommendations": []
        }
        
        if result.get("success"):
            # Calculate performance score
            analysis["score"] = self._calculate_score(result, hypothesis)
            
            # Compare with recent experiments
            analysis["comparison"] = self._compare_with_recent(result, recent_experiments)
            
            # Extract insights
            analysis["insights"] = self._extract_insights(result, hypothesis, analysis["comparison"])
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(
                result, hypothesis, analysis["insights"]
            )
        else:
            # Analyze failure
            analysis["failure_analysis"] = self._analyze_failure(result, hypothesis)
            
        return analysis
        
    def _calculate_score(self, result: Dict, hypothesis: Dict) -> float:
        """Calculate a performance score for the result"""
        
        score = 0.0
        metrics = result.get("metrics", {})
        
        # Base score for successful execution
        score += 1.0
        
        # Efficiency bonus
        exec_time = metrics.get("execution_time", float('inf'))
        if exec_time < 1.0:  # Fast execution
            score += 0.5
        elif exec_time > 10.0:  # Slow execution
            score -= 0.5
            
        # Memory efficiency
        memory_mb = metrics.get("memory_mb", float('inf'))
        if memory_mb < 100:  # Low memory usage
            score += 0.3
        elif memory_mb > 500:  # High memory usage
            score -= 0.3
            
        # Check if expected outcomes were met
        if self._check_expected_outcomes(result, hypothesis):
            score += 1.0
            
        # Novel results bonus
        if self._is_novel_result(result):
            score += 0.5
            
        return max(0.0, score)
        
    def _compare_with_recent(self, result: Dict, recent_experiments: List[Dict]) -> Dict:
        """Compare result with recent experiments"""
        
        comparison = {
            "better_than": 0,
            "worse_than": 0,
            "similar_to": 0,
            "performance_rank": 0,
            "is_improvement": False
        }
        
        if not recent_experiments:
            return comparison
            
        # Extract metrics for comparison
        current_metrics = result.get("metrics", {})
        current_time = current_metrics.get("execution_time", float('inf'))
        
        time_comparisons = []
        
        for exp in recent_experiments:
            exp_result = exp.get("result", {})
            if not exp_result.get("success"):
                continue
                
            exp_metrics = exp_result.get("metrics", {})
            exp_time = exp_metrics.get("execution_time", float('inf'))
            
            if exp_time != float('inf'):
                time_comparisons.append(exp_time)
                
                if current_time < exp_time * (1 - self.config.MIN_IMPROVEMENT_THRESHOLD):
                    comparison["better_than"] += 1
                elif current_time > exp_time * (1 + self.config.MIN_IMPROVEMENT_THRESHOLD):
                    comparison["worse_than"] += 1
                else:
                    comparison["similar_to"] += 1
                    
        # Calculate rank
        if time_comparisons and current_time != float('inf'):
            time_comparisons.append(current_time)
            time_comparisons.sort()
            comparison["performance_rank"] = time_comparisons.index(current_time) + 1
            comparison["is_improvement"] = comparison["performance_rank"] <= len(time_comparisons) // 2
            
        return comparison
        
    def _extract_insights(self, result: Dict, hypothesis: Dict, comparison: Dict) -> Dict:
        """Extract insights from the experimental result"""
        
        insights = {
            "key_findings": [],
            "patterns": [],
            "anomalies": [],
            "theoretical_implications": []
        }
        
        # Analyze output data
        output = result.get("output", {})
        
        if isinstance(output, dict):
            # Look for interesting patterns in output
            for key, value in output.items():
                if isinstance(value, (int, float)) and value > 0:
                    insights["key_findings"].append(f"{key}: {value}")
                    
        # Performance insights
        if comparison.get("is_improvement"):
            insights["key_findings"].append(
                f"Performance improvement: ranked {comparison['performance_rank']} among recent experiments"
            )
            
        # Use LLM for deeper analysis if configured
        if self.config.ANALYSIS_DEPTH in ["moderate", "deep"]:
            llm_insights = self._get_llm_insights(result, hypothesis)
            insights.update(llm_insights)
            
        return insights
        
    def _get_llm_insights(self, result: Dict, hypothesis: Dict) -> Dict:
        """Use LLM to extract deeper insights"""
        
        prompt = f"""Analyze this experimental result:

Hypothesis: {hypothesis['description']}
Expected outcome: {hypothesis.get('expected_outcome', 'Not specified')}

Result:
Success: {result.get('success', False)}
Output: {json.dumps(result.get('output', 'No output'), indent=2)[:500]}
Metrics: {json.dumps(result.get('metrics', {}), indent=2)}

Extract:
1. Key findings (what worked or didn't work)
2. Patterns observed in the data
3. Theoretical implications
4. Suggestions for next experiments

Format as JSON."""

        try:
            response = call_llm(
                prompt,
                temperature=0.3,
                provider=self.config.MODEL_PROVIDER,
                model=self.config.MODEL_NAME
            )
            
            # Try to parse as JSON
            try:
                llm_insights = json.loads(response)
                return llm_insights
            except:
                # Fallback: extract what we can
                return {"llm_analysis": response[:500]}
                
        except Exception as e:
            print(f"LLM insight extraction failed: {e}")
            return {}
            
    def _generate_recommendations(self, result: Dict, hypothesis: Dict, 
                                insights: Dict) -> List[str]:
        """Generate recommendations for future experiments"""
        
        recommendations = []
        
        # Based on performance
        metrics = result.get("metrics", {})
        if metrics.get("execution_time", float('inf')) > 5:
            recommendations.append("Consider optimization techniques to reduce execution time")
            
        if metrics.get("memory_mb", 0) > 200:
            recommendations.append("Explore memory-efficient alternatives")
            
        # Based on insights
        if insights.get("key_findings"):
            recommendations.append(f"Build upon findings: {insights['key_findings'][0]}")
            
        # Based on hypothesis type
        if "optimization" in hypothesis.get("approach", "").lower():
            recommendations.append("Test with larger datasets to validate optimization")
            
        return recommendations
        
    def _check_expected_outcomes(self, result: Dict, hypothesis: Dict) -> bool:
        """Check if expected outcomes were achieved"""
        
        expected = hypothesis.get("expected_outcome", "").lower()
        output = str(result.get("output", "")).lower()
        
        # Simple keyword matching
        keywords = ["improve", "better", "faster", "efficient", "pattern", "found"]
        
        return any(keyword in expected and keyword in output for keyword in keywords)
        
    def _is_novel_result(self, result: Dict) -> bool:
        """Check if result contains novel findings"""
        
        # Simple heuristic: check if output contains unexpected values
        output = result.get("output", {})
        
        if isinstance(output, dict):
            # Check for unusual keys or values
            unusual_keys = [k for k in output.keys() if k not in ["result", "time", "data"]]
            return len(unusual_keys) > 0
            
        return False
        
    def _analyze_failure(self, result: Dict, hypothesis: Dict) -> Dict:
        """Analyze why an experiment failed"""
        
        failure_analysis = {
            "error_type": "unknown",
            "likely_cause": "",
            "suggestions": []
        }
        
        error = result.get("error", "")
        
        if "timeout" in error.lower():
            failure_analysis["error_type"] = "timeout"
            failure_analysis["likely_cause"] = "Algorithm complexity too high"
            failure_analysis["suggestions"] = [
                "Reduce problem size",
                "Optimize algorithm",
                "Increase timeout limit"
            ]
        elif "memory" in error.lower():
            failure_analysis["error_type"] = "memory"
            failure_analysis["likely_cause"] = "Excessive memory usage"
            failure_analysis["suggestions"] = [
                "Use memory-efficient data structures",
                "Process data in chunks",
                "Reduce data size"
            ]
        elif "syntax" in error.lower() or "name" in error.lower():
            failure_analysis["error_type"] = "code_error"
            failure_analysis["likely_cause"] = "Code generation issue"
            failure_analysis["suggestions"] = [
                "Improve code generation prompts",
                "Add better error handling",
                "Validate generated code"
            ]
            
        return failure_analysis
        
    def summarize_iteration(self, iteration_results: List[Dict]) -> str:
        """Generate summary of an iteration"""
        
        if not iteration_results:
            return "No experiments completed in this iteration."
            
        # Calculate statistics
        total = len(iteration_results)
        successful = sum(1 for r in iteration_results if r["result"].get("success", False))
        
        # Get best result
        best_result = None
        best_score = -1
        
        for exp in iteration_results:
            score = exp.get("analysis", {}).get("score", 0)
            if score > best_score:
                best_score = score
                best_result = exp
                
        # Build summary
        summary_parts = [
            f"Completed {total} experiments ({successful} successful)",
            f"Success rate: {successful/total*100:.1f}%"
        ]
        
        if best_result:
            summary_parts.append(
                f"Best result: {best_result['hypothesis']['description'][:50]}... (score: {best_score:.2f})"
            )
            
        # Extract common patterns
        all_insights = []
        for exp in iteration_results:
            insights = exp.get("analysis", {}).get("insights", {})
            all_insights.extend(insights.get("key_findings", []))
            
        if all_insights:
            summary_parts.append(f"Key insights: {'; '.join(all_insights[:3])}")
            
        return " | ".join(summary_parts)