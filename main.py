#!/usr/bin/env python3
"""
Toy ASI-ARCH: Main orchestrator for autonomous research system
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

from config import Config
from researcher import Researcher
from engineer import Engineer
from analyst import Analyst
from cognition_base import CognitionBase
from utils import setup_logging, ensure_directories, display_banner

class ToyASIARCH:
    """Main orchestrator for the research system"""
    
    def __init__(self):
        self.config = Config()
        self.setup_workspace()
        self.setup_logging()
        
        # Initialize components
        self.cognition_base = CognitionBase(self.config)
        self.researcher = Researcher(self.config, self.cognition_base)
        self.engineer = Engineer(self.config)
        self.analyst = Analyst(self.config, self.cognition_base)
        
        self.current_state = self.load_state()
        
    def setup_workspace(self):
        """Create necessary directories"""
        ensure_directories([
            self.config.WORKSPACE_DIR,
            self.config.COGNITIONS_DIR,
            self.config.EXPERIMENTS_DIR,
            self.config.TEMP_DIR
        ])
        
    def setup_logging(self):
        """Configure logging"""
        self.logger = setup_logging(
            log_file=self.config.WORKSPACE_DIR / "research_log.txt",
            level=self.config.LOG_LEVEL
        )
        
    def load_state(self):
        """Load previous research state if exists"""
        state_file = self.config.WORKSPACE_DIR / "current_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return {
            "iteration": 0,
            "total_experiments": 0,
            "best_results": [],
            "research_objective": None
        }
        
    def save_state(self):
        """Save current research state"""
        state_file = self.config.WORKSPACE_DIR / "current_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
            
    def get_research_objective(self):
        """Get research objective from user"""
        print("\n" + "="*60)
        print("TOY ASI-ARCH: Autonomous Research System")
        print("="*60)
        
        if self.current_state["research_objective"]:
            print(f"\nContinuing research: {self.current_state['research_objective']}")
            cont = input("Continue with this objective? (y/n): ").lower()
            if cont == 'y':
                return self.current_state["research_objective"]
                
        print("\nExamples of research objectives:")
        print("- Find efficient algorithms for detecting prime numbers")
        print("- Optimize bubble sort for nearly sorted arrays")
        print("- Develop heuristics for solving 8-puzzle problems")
        print("- Create compression algorithms for text data")
        
        objective = input("\nEnter your research objective: ").strip()
        if not objective:
            print("No objective provided. Exiting.")
            sys.exit(0)
            
        self.current_state["research_objective"] = objective
        self.save_state()
        return objective
        
    def research_iteration(self):
        """Execute one complete research iteration"""
        iteration = self.current_state["iteration"]
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"ITERATION {iteration}")
        self.logger.info(f"{'='*50}")
        
        # Get recent experiments for context
        recent_experiments = self.get_recent_experiments()
        
        # Generate hypotheses
        self.logger.info("Generating hypotheses...")
        hypotheses = self.researcher.generate_hypotheses(
            self.current_state["research_objective"],
            recent_experiments
        )
        
        iteration_results = []
        
        # Execute experiments
        for i, hypothesis in enumerate(hypotheses[:self.config.EXPERIMENTS_PER_ITERATION]):
            self.logger.info(f"\nExperiment {i+1}/{len(hypotheses)}")
            self.logger.info(f"Hypothesis: {hypothesis['description']}")
            
            # Execute experiment
            result = self.engineer.execute_experiment(hypothesis)
            
            # Quick analysis
            analysis = self.analyst.analyze_result(
                result,
                hypothesis,
                recent_experiments
            )
            
            # Store complete experiment record
            experiment = {
                "id": f"exp_{iteration}_{i}",
                "timestamp": datetime.now().isoformat(),
                "iteration": iteration,
                "hypothesis": hypothesis,
                "result": result,
                "analysis": analysis
            }
            
            self.save_experiment(experiment)
            iteration_results.append(experiment)
            
            # Update cognition base with insights
            if analysis.get("insights"):
                self.cognition_base.add_insight(analysis["insights"])
                
            self.logger.info(f"Result: {result.get('summary', 'No summary')}")
            
        # Iteration summary
        self.logger.info("\nIteration Summary:")
        summary = self.analyst.summarize_iteration(iteration_results)
        self.logger.info(summary)
        
        # Update state
        self.current_state["iteration"] += 1
        self.current_state["total_experiments"] += len(iteration_results)
        self.update_best_results(iteration_results)
        self.save_state()
        
    def get_recent_experiments(self, n=10):
        """Get n most recent experiments"""
        exp_dir = Path(self.config.EXPERIMENTS_DIR)
        experiments = []
        
        for exp_file in sorted(exp_dir.glob("*.json"), reverse=True)[:n]:
            with open(exp_file, 'r') as f:
                experiments.append(json.load(f))
                
        return experiments
        
    def save_experiment(self, experiment):
        """Save experiment to file"""
        filename = f"{experiment['id']}.json"
        filepath = Path(self.config.EXPERIMENTS_DIR) / filename
        
        with open(filepath, 'w') as f:
            json.dump(experiment, f, indent=2)
            
    def update_best_results(self, new_results):
        """Update list of best results"""
        # Simple scoring based on analysis
        for result in new_results:
            score = result.get("analysis", {}).get("score", 0)
            if score > 0:
                self.current_state["best_results"].append({
                    "id": result["id"],
                    "score": score,
                    "description": result["hypothesis"]["description"]
                })
                
        # Keep top 20
        self.current_state["best_results"].sort(
            key=lambda x: x["score"], 
            reverse=True
        )
        self.current_state["best_results"] = self.current_state["best_results"][:20]
        
    def run(self):
        """Main execution loop"""
        display_banner()
        
        # Get research objective
        objective = self.get_research_objective()
        self.logger.info(f"Research Objective: {objective}")
        
        print(f"\nStarting research on: {objective}")
        print(f"Check research_workspace/research_log.txt for progress")
        print("Press Ctrl+C to pause at any time\n")
        
        try:
            while self.current_state["iteration"] < self.config.MAX_ITERATIONS:
                self.research_iteration()
                
                # Pause between iterations
                if self.config.ITERATION_DELAY > 0:
                    time.sleep(self.config.ITERATION_DELAY)
                    
        except KeyboardInterrupt:
            print("\n\nResearch paused. Progress saved.")
            print("Run again to continue from where you left off.")
            
        except Exception as e:
            self.logger.error(f"Error during research: {str(e)}", exc_info=True)
            print(f"\nError occurred: {str(e)}")
            print("Check research_log.txt for details")
            
        finally:
            self.save_state()
            self.generate_final_report()
            
    def generate_final_report(self):
        """Generate summary report of research"""
        report_file = self.config.WORKSPACE_DIR / "research_report.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"RESEARCH REPORT\n")
            f.write(f"="*60 + "\n\n")
            f.write(f"Objective: {self.current_state['research_objective']}\n")
            f.write(f"Total Iterations: {self.current_state['iteration']}\n")
            f.write(f"Total Experiments: {self.current_state['total_experiments']}\n\n")
            
            f.write("TOP DISCOVERIES:\n")
            f.write("-"*40 + "\n")
            for i, result in enumerate(self.current_state["best_results"][:10]):
                f.write(f"{i+1}. {result['description']} (Score: {result['score']:.2f})\n")
                
        print(f"\nResearch report saved to: {report_file}")

if __name__ == "__main__":
    system = ToyASIARCH()
    system.run()