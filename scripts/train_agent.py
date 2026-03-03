#!/usr/bin/env python3
"""
train_agent.py - Analyze agent performance and recommend updates

This script analyzes the knowledge base and current agent performance
to determine if the agent needs updates. It provides specific recommendations
and can automatically update agent version/configuration.

Usage:
    ./scripts/train_agent.py --issue 25
    ./scripts/train_agent.py --analyze-all
    ./scripts/train_agent.py --recommend
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class AgentTrainer:
    """Analyze agent performance and recommend updates."""
    
    def __init__(self, kb_dir: Path = Path("agents/knowledge")):
        self.kb_dir = kb_dir
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load all knowledge base files."""
        self.workflow_patterns = self._load_json("workflow_patterns.json")
        self.problem_solutions = self._load_json("problem_solutions.json")
        self.time_estimates = self._load_json("time_estimates.json")
        self.command_sequences = self._load_json("command_sequences.json")
        self.agent_metrics = self._load_json("agent_metrics.json")
    
    def _load_json(self, filename: str) -> Dict:
        """Load a JSON file from knowledge base."""
        filepath = self.kb_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath) as f:
            return json.load(f)
    
    def _save_json(self, filename: str, data: Dict):
        """Save data to JSON file in knowledge base."""
        filepath = self.kb_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def analyze_after_issue(self, issue_num: int) -> List[Dict]:
        """Analyze what updates are needed after completing an issue."""
        print(f"🔍 Analyzing agent after Issue #{issue_num}\n")
        
        recommendations = []
        
        # Load issue learnings
        learnings_file = self.kb_dir.parent / "training" / "learnings" / f"issue-{issue_num}-learnings.json"
        if not learnings_file.exists():
            print(f"❌ No learnings found for Issue #{issue_num}")
            print(f"   Run: ./scripts/extract_learnings.py --export <export-file>")
            return []
        
        with open(learnings_file) as f:
            learnings = json.load(f)
        
        # Check for new problems
        new_problems = self._analyze_new_problems(learnings)
        if new_problems:
            recommendations.append({
                "priority": "high" if new_problems['count'] >= 2 else "medium",
                "agent": "workflow_agent",
                "update_type": "problem_detection",
                "description": f"Add {new_problems['count']} new problem detection patterns",
                "details": new_problems['problems'],
                "effort_minutes": 30 if new_problems['count'] >= 2 else 15
            })
        
        # Check time estimation accuracy
        time_variance = self._analyze_time_variance()
        if time_variance['needs_update']:
            recommendations.append({
                "priority": "medium",
                "agent": "workflow_agent",
                "update_type": "time_estimation",
                "description": f"Adjust time multiplier: {time_variance['old']:.3f} → {time_variance['new']:.3f}",
                "details": f"Variance: {time_variance['variance']:.1%}",
                "effort_minutes": 10
            })
        
        # Check for new command patterns
        new_commands = self._analyze_new_commands(learnings)
        if new_commands['count'] > 0:
            recommendations.append({
                "priority": "low",
                "agent": "workflow_agent",
                "update_type": "command_sequences",
                "description": f"Add {new_commands['count']} new command sequences",
                "details": new_commands['categories'],
                "effort_minutes": 20
            })
        
        # Check if workflow pattern changed significantly
        workflow_change = self._analyze_workflow_changes(learnings)
        if workflow_change['significant']:
            recommendations.append({
                "priority": "critical",
                "agent": "NEW AGENT NEEDED",
                "update_type": "new_agent",
                "description": "Workflow pattern significantly different from standard",
                "details": workflow_change['differences'],
                "effort_minutes": 120
            })
        
        # Display recommendations
        self._display_recommendations(recommendations)
        
        # Update agent metrics with recommendations
        self._update_agent_recommendations(recommendations)
        
        return recommendations
    
    def analyze_all(self) -> Dict:
        """Analyze overall agent performance across all issues."""
        print("🔍 Analyzing agent performance across all issues\n")
        
        analysis = {
            "total_issues": len(self.workflow_patterns.get('issues', [])),
            "total_problems": len(self.problem_solutions.get('problems', [])),
            "confidence_level": self.agent_metrics.get('knowledge_base_status', {}).get('confidence_level', 'none'),
            "time_accuracy": self._calculate_time_accuracy(),
            "problem_coverage": self._calculate_problem_coverage(),
            "agent_maturity": self._calculate_agent_maturity(),
            "readiness": self._assess_readiness()
        }
        
        self._display_overall_analysis(analysis)
        
        return analysis
    
    def recommend_updates(self) -> List[Dict]:
        """Get all pending update recommendations."""
        print("📋 Current update recommendations\n")
        
        recommendations = self.agent_metrics.get('agents', {}).get('workflow_agent', {}).get('update_recommendations', [])
        
        if not recommendations:
            print("✅ No pending updates needed")
            return []
        
        # Group by priority
        by_priority = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for rec in recommendations:
            priority = rec.get('priority', 'low')
            by_priority[priority].append(rec)
        
        # Display by priority
        for priority in ['critical', 'high', 'medium', 'low']:
            recs = by_priority[priority]
            if recs:
                print(f"\n{priority.upper()} Priority ({len(recs)} items):")
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec['description']}")
                    print(f"     Agent: {rec['agent']}")
                    print(f"     Effort: ~{rec.get('effort_minutes', 0)} minutes")
        
        # Calculate total effort
        total_effort = sum(rec.get('effort_minutes', 0) for rec in recommendations)
        print(f"\n📊 Total improvement effort: ~{total_effort} minutes ({total_effort/60:.1f} hours)")
        
        return recommendations
    
    def _analyze_new_problems(self, learnings: Dict) -> Dict:
        """Check if issue introduced new problem patterns."""
        existing_problems = {p['problem'] for p in self.problem_solutions.get('problems', [])}
        new_problems_list = []
        
        for problem in learnings.get('problems_solved', []):
            if problem['problem'] not in existing_problems:
                new_problems_list.append({
                    "problem": problem['problem'],
                    "solution": problem['solution'],
                    "category": problem['category']
                })
        
        return {
            "count": len(new_problems_list),
            "problems": new_problems_list
        }
    
    def _analyze_time_variance(self) -> Dict:
        """Check if time estimation model needs adjustment."""
        stats = self.time_estimates.get('statistics', {})
        current_multiplier = stats.get('avg_multiplier', 1.0)
        sample_size = stats.get('sample_size', 0)
        
        if sample_size < 2:
            return {"needs_update": False}
        
        # Get recent issues (last 5)
        recent_issues = self.time_estimates.get('completed_issues', [])[-5:]
        recent_multipliers = [issue['multiplier'] for issue in recent_issues if issue['multiplier'] > 0]
        
        if not recent_multipliers:
            return {"needs_update": False}
        
        recent_avg = statistics.mean(recent_multipliers)
        variance = abs(recent_avg - current_multiplier) / current_multiplier
        
        threshold = self.agent_metrics.get('update_thresholds', {}).get('time_variance_threshold', 0.1)
        
        return {
            "needs_update": variance > threshold,
            "old": current_multiplier,
            "new": recent_avg,
            "variance": variance
        }
    
    def _analyze_new_commands(self, learnings: Dict) -> Dict:
        """Check for new reusable command patterns."""
        existing_commands = set()
        for category, cmds in self.command_sequences.get('reusable_commands', {}).items():
            existing_commands.update(cmds)
        
        new_by_category = {}
        for cmd in learnings.get('command_sequences', []):
            if cmd['command'] not in existing_commands:
                category = cmd['category']
                if category not in new_by_category:
                    new_by_category[category] = []
                new_by_category[category].append(cmd['command'])
        
        total_new = sum(len(cmds) for cmds in new_by_category.values())
        
        return {
            "count": total_new,
            "categories": new_by_category
        }
    
    def _analyze_workflow_changes(self, learnings: Dict) -> Dict:
        """Check if workflow pattern is significantly different."""
        standard_phases = set(self.workflow_patterns.get('common_phases', []))
        issue_phases = {phase['name'] for phase in learnings.get('workflow_phases', [])}
        
        # Check phase overlap
        overlap = len(standard_phases & issue_phases)
        total = len(standard_phases | issue_phases)
        
        similarity = overlap / total if total > 0 else 0
        
        # Consider significantly different if less than 60% similarity
        significant = similarity < 0.6
        
        differences = []
        if significant:
            new_phases = issue_phases - standard_phases
            missing_phases = standard_phases - issue_phases
            
            if new_phases:
                differences.append(f"New phases: {', '.join(new_phases)}")
            if missing_phases:
                differences.append(f"Missing phases: {', '.join(missing_phases)}")
        
        return {
            "significant": significant,
            "similarity": similarity,
            "differences": differences
        }
    
    def _calculate_time_accuracy(self) -> float:
        """Calculate time estimation accuracy."""
        completed = self.time_estimates.get('completed_issues', [])
        if not completed:
            return 0.0
        
        # Calculate average absolute error
        errors = []
        for issue in completed:
            if issue['estimated_hours'] > 0:
                error = abs(issue['actual_hours'] - issue['estimated_hours']) / issue['estimated_hours']
                errors.append(error)
        
        if not errors:
            return 0.0
        
        avg_error = statistics.mean(errors)
        accuracy = max(0.0, 1.0 - avg_error)
        
        return accuracy
    
    def _calculate_problem_coverage(self) -> float:
        """Calculate percentage of problems that have documented solutions."""
        problems = self.problem_solutions.get('problems', [])
        if not problems:
            return 0.0
        
        with_solutions = sum(1 for p in problems if p.get('solution') and p['solution'] != "Not documented")
        coverage = with_solutions / len(problems)
        
        return coverage
    
    def _calculate_agent_maturity(self) -> str:
        """Calculate overall agent maturity level."""
        issue_count = len(self.workflow_patterns.get('issues', []))
        problem_count = len(self.problem_solutions.get('problems', []))
        time_accuracy = self._calculate_time_accuracy()
        
        score = 0
        
        # Issue count (max 40 points)
        if issue_count >= 20:
            score += 40
        elif issue_count >= 10:
            score += 30
        elif issue_count >= 5:
            score += 20
        elif issue_count >= 2:
            score += 10
        
        # Problem database (max 30 points)
        if problem_count >= 20:
            score += 30
        elif problem_count >= 10:
            score += 20
        elif problem_count >= 5:
            score += 15
        elif problem_count >= 2:
            score += 10
        
        # Time accuracy (max 30 points)
        score += int(time_accuracy * 30)
        
        # Determine maturity level
        if score >= 80:
            return "mature"
        elif score >= 60:
            return "developing"
        elif score >= 40:
            return "learning"
        elif score >= 20:
            return "initial"
        else:
            return "nascent"
    
    def _assess_readiness(self) -> Dict:
        """Assess if agent is ready for production use."""
        issue_count = len(self.workflow_patterns.get('issues', []))
        confidence_threshold = self.agent_metrics.get('update_thresholds', {}).get('confidence_threshold', 20)
        time_accuracy = self._calculate_time_accuracy()
        problem_coverage = self._calculate_problem_coverage()
        
        ready = (
            issue_count >= confidence_threshold and
            time_accuracy >= 0.8 and
            problem_coverage >= 0.7
        )
        
        blockers = []
        if issue_count < confidence_threshold:
            blockers.append(f"Need {confidence_threshold - issue_count} more issues for confidence")
        if time_accuracy < 0.8:
            blockers.append(f"Time accuracy too low: {time_accuracy:.1%} (need ≥80%)")
        if problem_coverage < 0.7:
            blockers.append(f"Problem coverage too low: {problem_coverage:.1%} (need ≥70%)")
        
        return {
            "ready": ready,
            "blockers": blockers
        }
    
    def _display_recommendations(self, recommendations: List[Dict]):
        """Display recommendations in a formatted way."""
        if not recommendations:
            print("✅ No updates needed at this time")
            return
        
        print(f"📊 Analysis Complete - {len(recommendations)} recommendations\n")
        
        # Group by priority
        by_priority = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for rec in recommendations:
            priority = rec.get('priority', 'low')
            by_priority[priority].append(rec)
        
        # Display
        for priority in ['critical', 'high', 'medium', 'low']:
            recs = by_priority[priority]
            if not recs:
                continue
            
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[priority]
            print(f"{icon} {priority.upper()} Priority:")
            
            for i, rec in enumerate(recs, 1):
                print(f"\n  {i}. Update {rec['agent']}")
                print(f"     Action: {rec['description']}")
                print(f"     Type: {rec['update_type']}")
                print(f"     Effort: ~{rec.get('effort_minutes', 0)} minutes")
                
                if rec.get('details'):
                    if isinstance(rec['details'], list):
                        print(f"     Details:")
                        for detail in rec['details'][:3]:  # Show first 3
                            if isinstance(detail, dict):
                                print(f"       • {detail.get('problem', detail)}")
                            else:
                                print(f"       • {detail}")
                        if len(rec['details']) > 3:
                            print(f"       ... and {len(rec['details']) - 3} more")
                    else:
                        print(f"     Details: {rec['details']}")
        
        # Total effort
        total_effort = sum(rec.get('effort_minutes', 0) for rec in recommendations)
        print(f"\n📈 Total improvement effort: ~{total_effort} minutes ({total_effort/60:.1f} hours)")
        
        # Expected benefits
        high_priority_count = len(by_priority['high']) + len(by_priority['critical'])
        if high_priority_count > 0:
            print(f"💡 Expected benefits: Prevent {high_priority_count} known issue types in future runs")
    
    def _display_overall_analysis(self, analysis: Dict):
        """Display overall agent analysis."""
        print(f"📊 Agent Performance Analysis\n")
        print(f"Training Data:")
        print(f"  • Issues analyzed: {analysis['total_issues']}")
        print(f"  • Problems cataloged: {analysis['total_problems']}")
        print(f"  • Confidence level: {analysis['confidence_level']}")
        
        print(f"\nPerformance Metrics:")
        print(f"  • Time estimation accuracy: {analysis['time_accuracy']:.1%}")
        print(f"  • Problem solution coverage: {analysis['problem_coverage']:.1%}")
        print(f"  • Agent maturity: {analysis['agent_maturity']}")
        
        print(f"\nReadiness Assessment:")
        if analysis['readiness']['ready']:
            print(f"  ✅ Agent is ready for production use")
        else:
            print(f"  ⚠️  Agent not yet ready for production")
            for blocker in analysis['readiness']['blockers']:
                print(f"     • {blocker}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if analysis['total_issues'] < 5:
            print(f"  • Complete {5 - analysis['total_issues']} more issues to reach minimum confidence")
        elif analysis['total_issues'] < 20:
            print(f"  • Complete {20 - analysis['total_issues']} more issues to reach high confidence")
        else:
            print(f"  • Consider creating specialized agents for different workflow types")
        
        if analysis['time_accuracy'] < 0.8:
            print(f"  • Focus on accurate time tracking to improve estimation model")
        
        if analysis['problem_coverage'] < 0.7:
            print(f"  • Document solutions for {int((0.7 - analysis['problem_coverage']) * analysis['total_problems'])} more problems")
    
    def _update_agent_recommendations(self, recommendations: List[Dict]):
        """Save recommendations to agent metrics."""
        self.agent_metrics['agents']['workflow_agent']['update_recommendations'] = recommendations
        self.agent_metrics['last_updated'] = datetime.now().isoformat()
        
        self._save_json("agent_metrics.json", self.agent_metrics)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze agent performance and recommend updates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--issue', type=int,
                        help='Analyze after completing specific issue')
    parser.add_argument('--analyze-all', action='store_true',
                        help='Analyze overall agent performance')
    parser.add_argument('--recommend', action='store_true',
                        help='Show current update recommendations')
    parser.add_argument('--kb-dir', type=str, default='agents/knowledge',
                        help='Knowledge base directory')
    
    args = parser.parse_args()
    
    trainer = AgentTrainer(kb_dir=Path(args.kb_dir))
    
    if args.issue:
        recommendations = trainer.analyze_after_issue(args.issue)
        
        if recommendations:
            print(f"\n📝 Next steps:")
            print(f"  1. Review recommendations above")
            print(f"  2. Update agent code if needed")
            print(f"  3. Run: ./scripts/train_agent.py --recommend  # to see all pending updates")
    
    elif args.analyze_all:
        analysis = trainer.analyze_all()
    
    elif args.recommend:
        recommendations = trainer.recommend_updates()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
