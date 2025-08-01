"""
Cognition Base: Knowledge management system
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from utils import calculate_similarity, call_llm

class CognitionBase:
    """Manages knowledge storage and retrieval"""
    
    def __init__(self, config):
        self.config = config
        self.insights_file = config.COGNITIONS_DIR / "insights.json"
        self.patterns_file = config.COGNITIONS_DIR / "patterns.json"
        self.knowledge_file = config.COGNITIONS_DIR / "knowledge.json"
        
        self._load_knowledge()
        
    def _load_knowledge(self):
        """Load existing knowledge from files"""
        self.insights = self._load_json(self.insights_file, default=[])
        self.patterns = self._load_json(self.patterns_file, default={})
        self.knowledge = self._load_json(self.knowledge_file, default={
            "algorithms": {},
            "optimizations": {},
            "failures": {}
        })
        
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file with default value"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return default
        return default
        
    def _save_json(self, data: Any, filepath: Path):
        """Save data to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def add_insight(self, insight: Dict):
        """Add new insight to knowledge base"""
        
        # Create insight record
        insight_record = {
            "id": self._generate_id(str(insight)),
            "timestamp": datetime.now().isoformat(),
            "content": insight,
            "relevance_score": 1.0,
            "usage_count": 0
        }
        
        # Check for duplicates
        if not self._is_duplicate_insight(insight_record):
            self.insights.append(insight_record)
            
            # Keep only most recent insights
            if len(self.insights) > self.config.MAX_INSIGHTS_STORED:
                # Sort by relevance and recency
                self.insights.sort(
                    key=lambda x: (x["relevance_score"], x["timestamp"]), 
                    reverse=True
                )
                self.insights = self.insights[:self.config.MAX_INSIGHTS_STORED]
                
            self._save_json(self.insights, self.insights_file)
            
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()[:8]
        
    def _is_duplicate_insight(self, new_insight: Dict) -> bool:
        """Check if insight already exists"""
        new_content = str(new_insight["content"])
        
        for existing in self.insights:
            if calculate_similarity(str(existing["content"]), new_content) > 0.9:
                return True
                
        return False
        
    def get_relevant_insights(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve insights relevant to query"""
        
        if not self.insights:
            return []
            
        # Calculate relevance scores
        scored_insights = []
        
        for insight in self.insights:
            score = calculate_similarity(
                query.lower(), 
                str(insight["content"]).lower()
            )
            
            if score > self.config.INSIGHT_RELEVANCE_THRESHOLD:
                scored_insights.append({
                    "insight": insight["content"],
                    "relevance": score,
                    "timestamp": insight["timestamp"]
                })
                
                # Update usage count
                insight["usage_count"] += 1
                
        # Sort by relevance
        scored_insights.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Update relevance scores based on usage
        self._update_relevance_scores()
        
        return scored_insights[:limit]
        
    def _update_relevance_scores(self):
        """Update relevance scores based on usage patterns"""
        
        for insight in self.insights:
            # Decay old insights
            days_old = (datetime.now() - datetime.fromisoformat(insight["timestamp"])).days
            age_factor = 0.95 ** (days_old / 7)  # Decay by 5% per week
            
            # Boost frequently used insights
            usage_factor = 1 + (insight["usage_count"] * 0.1)
            
            insight["relevance_score"] = age_factor * usage_factor
            
    def add_pattern(self, pattern_type: str, pattern: Dict):
        """Add discovered pattern to knowledge base"""
        
        if pattern_type not in self.patterns:
            self.patterns[pattern_type] = []
            
        pattern_record = {
            "id": self._generate_id(str(pattern)),
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "occurrences": 1
        }
        
        # Check if pattern exists
        existing = self._find_similar_pattern(pattern_type, pattern)
        
        if existing:
            existing["occurrences"] += 1
        else:
            self.patterns[pattern_type].append(pattern_record)
            
        self._save_json(self.patterns, self.patterns_file)
        
    def _find_similar_pattern(self, pattern_type: str, pattern: Dict) -> Optional[Dict]:
        """Find similar existing pattern"""
        
        if pattern_type not in self.patterns:
            return None
            
        pattern_str = str(pattern)
        
        for existing in self.patterns[pattern_type]:
            if calculate_similarity(str(existing["pattern"]), pattern_str) > 0.8:
                return existing
                
        return None
        
    def get_patterns(self, pattern_type: str, min_occurrences: int = 2) -> List[Dict]:
        """Get patterns of specific type"""
        
        if pattern_type not in self.patterns:
            return []
            
        # Filter by minimum occurrences
        patterns = [
            p for p in self.patterns[pattern_type]
            if p["occurrences"] >= min_occurrences
        ]
        
        # Sort by occurrences
        patterns.sort(key=lambda x: x["occurrences"], reverse=True)
        
        return patterns
        
    def add_algorithm(self, name: str, description: str, code: str, performance: Dict):
        """Add successful algorithm to knowledge base"""
        
        algorithm = {
            "name": name,
            "description": description,
            "code": code,
            "performance": performance,
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.knowledge["algorithms"][name] = algorithm
        self._save_json(self.knowledge, self.knowledge_file)
        
    def get_algorithm(self, name: str) -> Optional[Dict]:
        """Retrieve algorithm by name"""
        return self.knowledge["algorithms"].get(name)
        
    def search_algorithms(self, query: str) -> List[Dict]:
        """Search algorithms by description"""
        
        results = []
        
        for name, algo in self.knowledge["algorithms"].items():
            score = calculate_similarity(
                query.lower(),
                (algo["description"] + " " + name).lower()
            )
            
            if score > 0.5:
                results.append({
                    "name": name,
                    "algorithm": algo,
                    "relevance": score
                })
                
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
        
    def add_failure(self, error_type: str, description: str, solution: Optional[str] = None):
        """Record failure pattern and solution"""
        
        if error_type not in self.knowledge["failures"]:
            self.knowledge["failures"][error_type] = []
            
        failure = {
            "description": description,
            "solution": solution,
            "timestamp": datetime.now().isoformat(),
            "occurrences": 1
        }
        
        # Check for similar failures
        similar = None
        for existing in self.knowledge["failures"][error_type]:
            if calculate_similarity(existing["description"], description) > 0.8:
                similar = existing
                break
                
        if similar:
            similar["occurrences"] += 1
            if solution and not similar["solution"]:
                similar["solution"] = solution
        else:
            self.knowledge["failures"][error_type].append(failure)
            
        self._save_json(self.knowledge, self.knowledge_file)
        
    def get_failure_solutions(self, error_description: str) -> List[Dict]:
        """Get solutions for similar failures"""
        
        solutions = []
        
        for error_type, failures in self.knowledge["failures"].items():
            for failure in failures:
                score = calculate_similarity(
                    error_description.lower(),
                    failure["description"].lower()
                )
                
                if score > 0.6 and failure.get("solution"):
                    solutions.append({
                        "error_type": error_type,
                        "solution": failure["solution"],
                        "relevance": score,
                        "occurrences": failure["occurrences"]
                    })
                    
        solutions.sort(key=lambda x: (x["relevance"], x["occurrences"]), reverse=True)
        return solutions
        
    def summarize_knowledge(self) -> Dict:
        """Generate summary of current knowledge"""
        
        summary = {
            "total_insights": len(self.insights),
            "pattern_types": list(self.patterns.keys()),
            "total_patterns": sum(len(p) for p in self.patterns.values()),
            "algorithms_stored": len(self.knowledge["algorithms"]),
            "failure_types": len(self.knowledge["failures"]),
            "most_used_insights": [],
            "common_patterns": []
        }
        
        # Most used insights
        if self.insights:
            sorted_insights = sorted(
                self.insights,
                key=lambda x: x["usage_count"],
                reverse=True
            )
            summary["most_used_insights"] = [
                {
                    "content": i["content"],
                    "usage_count": i["usage_count"]
                }
                for i in sorted_insights[:5]
            ]
            
        # Common patterns
        for pattern_type, patterns in self.patterns.items():
            if patterns:
                most_common = max(patterns, key=lambda x: x["occurrences"])
                summary["common_patterns"].append({
                    "type": pattern_type,
                    "pattern": most_common["pattern"],
                    "occurrences": most_common["occurrences"]
                })
                
        return summary