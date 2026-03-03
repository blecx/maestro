#!/usr/bin/env python3
"""
extract_learnings.py - Extract structured learnings from chat exports

This script parses completed issue chat exports and extracts:
- Workflow phases and durations
- Problems encountered and solutions
- Command sequences used
- Time estimates and actuals
- Key principles and decisions

The learnings are merged into the knowledge base for agent training.

Usage:
    ./scripts/extract_learnings.py --export docs/chat/2026-01-18-issue25-complete-workflow.md
    ./scripts/extract_learnings.py --export docs/chat/*.md --batch
"""

import argparse
import json
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LearningsExtractor:
    """Extract structured learnings from chat exports."""
    
    def __init__(self, knowledge_base_dir: Path = Path("agents/knowledge")):
        self.kb_dir = knowledge_base_dir
        self.kb_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_from_export(self, export_file: Path) -> Dict:
        """Extract all learnings from a chat export."""
        print(f"📖 Extracting learnings from {export_file.name}")
        
        # Detect and load content based on file type
        content = self._load_export_content(export_file)
        
        if not content:
            print("   ❌ Could not load export content")
            return {}
        
        # Extract issue number
        issue_num = self._extract_issue_number(export_file.name, content)
        if not issue_num:
            print("   ⚠️  Could not determine issue number")
            return {}
        
        print(f"   Issue: #{issue_num}")
        
        # Extract all learnings
        learnings = {
            "issue_num": issue_num,
            "export_file": export_file.name,
            "extracted_date": datetime.now().isoformat(),
            "workflow_phases": self._extract_workflow_phases(content),
            "problems_solved": self._extract_problems(content),
            "command_sequences": self._extract_commands(content),
            "time_metrics": self._extract_time_metrics(content),
            "principles": self._extract_principles(content),
            "files_changed": self._extract_files_changed(content),
            "metrics": self._extract_metrics(content)
        }
        
        print(f"   ✅ Extracted {len(learnings['problems_solved'])} problems")
        print(f"   ✅ Extracted {len(learnings['command_sequences'])} command sequences")
        print(f"   ✅ Extracted {len(learnings['workflow_phases'])} workflow phases")
        
        return learnings
    
    def _load_export_content(self, export_file: Path) -> str:
        """Load export content, supporting multiple formats."""
        try:
            # Try as JSON first
            if export_file.suffix == '.json':
                with open(export_file) as f:
                    data = json.load(f)
                
                # Extract text content from JSON structure
                if isinstance(data, dict):
                    # Common JSON export formats
                    if 'content' in data:
                        return data['content']
                    elif 'transcript' in data:
                        return data['transcript']
                    elif 'messages' in data:
                        # Reconstruct from messages
                        messages = data['messages']
                        return '\n\n'.join(f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
                                          for msg in messages)
                
                # Fallback: convert entire JSON to string
                return json.dumps(data, indent=2)
            
            # Try as plain text/markdown
            else:
                with open(export_file, encoding='utf-8') as f:
                    return f.read()
        
        except UnicodeDecodeError:
            # Try different encoding
            try:
                with open(export_file, encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"   ⚠️  Could not decode file: {e}")
                return ""
        
        except json.JSONDecodeError:
            # Not valid JSON, try as text
            try:
                with open(export_file, encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"   ⚠️  Could not read file: {e}")
                return ""
        
        except Exception as e:
            print(f"   ⚠️  Error loading export: {e}")
            return ""
    
    def merge_into_knowledge_base(self, learnings: Dict):
        """Merge extracted learnings into knowledge base."""
        print(f"\n📚 Merging learnings into knowledge base...")
        
        issue_num = learnings['issue_num']
        
        # Update workflow patterns
        self._update_workflow_patterns(learnings)
        
        # Update problem solutions
        self._update_problem_solutions(learnings)
        
        # Update time estimates
        self._update_time_estimates(learnings)
        
        # Update command sequences
        self._update_command_sequences(learnings)
        
        # Update agent metrics
        self._update_agent_metrics(learnings)
        
        # Save issue-specific learnings
        learnings_file = self.kb_dir.parent / "training" / "learnings" / f"issue-{issue_num}-learnings.json"
        learnings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(learnings_file, 'w') as f:
            json.dump(learnings, f, indent=2)
        
        print(f"✅ Knowledge base updated")
    
    def _extract_issue_number(self, filename: str, content: str) -> Optional[int]:
        """Extract issue number from filename or content."""
        # Try filename first
        match = re.search(r'issue[- ]?(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Try content
        match = re.search(r'Issue #(\d+)', content)
        if match:
            return int(match.group(1))
        
        match = re.search(r'#(\d+)', content[:500])  # Check first 500 chars
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_workflow_phases(self, content: str) -> List[Dict]:
        """Extract workflow phases and their details."""
        phases = []
        
        # Look for phase headers
        phase_pattern = r'##\s+(Phase \d+|Step \d+)[:\s]+([^\n]+)'
        matches = re.finditer(phase_pattern, content, re.MULTILINE)
        
        for match in matches:
            phase_id = match.group(1)
            phase_name = match.group(2).strip()
            
            # Try to extract time spent
            phase_content = self._get_section_content(content, match.start())
            time_spent = self._extract_time_from_section(phase_content)
            
            phases.append({
                "id": phase_id,
                "name": phase_name,
                "time_spent_minutes": time_spent,
                "order": len(phases) + 1
            })
        
        return phases
    
    def _extract_problems(self, content: str) -> List[Dict]:
        """Extract problems and their solutions."""
        problems = []
        
        # Look for problem indicators
        problem_patterns = [
            r'Problem[:\s]+([^\n]+)',
            r'Issue[:\s]+([^\n]+)',
            r'Error[:\s]+([^\n]+)',
            r'Failed[:\s]+([^\n]+)',
            r'❌\s*([^\n]+)',
        ]
        
        solution_patterns = [
            r'Solution[:\s]+([^\n]+)',
            r'Fix[:\s]+([^\n]+)',
            r'Resolved by[:\s]+([^\n]+)',
            r'✅\s*([^\n]+)',
        ]
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for problem
            problem_text = None
            for pattern in problem_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    problem_text = match.group(1).strip()
                    break
            
            if problem_text:
                # Look for solution in next few lines
                solution_text = None
                for j in range(i + 1, min(i + 10, len(lines))):
                    solution_line = lines[j]
                    for pattern in solution_patterns:
                        match = re.search(pattern, solution_line, re.IGNORECASE)
                        if match:
                            solution_text = match.group(1).strip()
                            break
                    if solution_text:
                        break
                
                # Categorize problem
                category = self._categorize_problem(problem_text)
                
                problems.append({
                    "problem": problem_text,
                    "solution": solution_text or "Not documented",
                    "category": category,
                    "line": i + 1
                })
            
            i += 1
        
        return problems
    
    def _extract_commands(self, content: str) -> List[Dict]:
        """Extract command sequences from code blocks."""
        commands = []
        
        # Extract code blocks
        code_block_pattern = r'```(?:bash|sh|shell)?\n(.*?)```'
        matches = re.finditer(code_block_pattern, content, re.DOTALL)
        
        for match in matches:
            code = match.group(1).strip()
            
            # Split into individual commands
            for line in code.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Categorize command
                category = self._categorize_command(line)
                
                commands.append({
                    "command": line,
                    "category": category
                })
        
        return commands
    
    def _extract_time_metrics(self, content: str) -> Dict:
        """Extract time estimates and actuals."""
        metrics = {
            "estimated_hours": 0.0,
            "actual_hours": 0.0,
            "multiplier": 1.0,
            "phase_times": {}
        }
        
        # Look for time mentions
        time_pattern = r'(\d+(?:\.\d+)?)\s*(hour|hr|h|minute|min|m)'
        matches = re.finditer(time_pattern, content, re.IGNORECASE)
        
        total_minutes = 0
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            if unit in ['hour', 'hr', 'h']:
                total_minutes += value * 60
            else:  # minutes
                total_minutes += value
        
        if total_minutes > 0:
            metrics['actual_hours'] = total_minutes / 60
        
        # Look for estimate vs actual
        estimate_pattern = r'estimated?[:\s]+(\d+(?:\.\d+)?)\s*(?:hour|hr|h)'
        match = re.search(estimate_pattern, content, re.IGNORECASE)
        if match:
            metrics['estimated_hours'] = float(match.group(1))
        
        if metrics['estimated_hours'] > 0:
            metrics['multiplier'] = metrics['actual_hours'] / metrics['estimated_hours']
        
        return metrics
    
    def _extract_principles(self, content: str) -> List[str]:
        """Extract key principles and learnings."""
        principles = []
        
        # Look for principle indicators
        principle_patterns = [
            r'Principle[:\s]+([^\n]+)',
            r'Key learning[:\s]+([^\n]+)',
            r'Important[:\s]+([^\n]+)',
            r'Remember[:\s]+([^\n]+)',
            r'Always[:\s]+([^\n]+)',
            r'Never[:\s]+([^\n]+)',
        ]
        
        for pattern in principle_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                principle = match.group(1).strip()
                if principle and len(principle) > 10:  # Skip very short matches
                    principles.append(principle)
        
        return list(set(principles))  # Remove duplicates
    
    def _extract_files_changed(self, content: str) -> List[str]:
        """Extract list of files changed."""
        files = set()
        
        # Look for file paths
        file_pattern = r'(?:^|\s)([a-zA-Z0-9_\-./]+\.(py|js|ts|tsx|jsx|md|json|yaml|yml|sh|bash))'
        matches = re.finditer(file_pattern, content, re.MULTILINE)
        
        for match in matches:
            filepath = match.group(1)
            if '/' in filepath:  # Likely a real path
                files.add(filepath)
        
        return sorted(list(files))
    
    def _extract_metrics(self, content: str) -> Dict:
        """Extract various metrics from the export."""
        return {
            "total_lines": len(content.split('\n')),
            "total_chars": len(content),
            "code_blocks": len(re.findall(r'```', content)) // 2,
            "has_pr_number": bool(re.search(r'PR #\d+', content)),
            "has_completion": bool(re.search(r'(completed|merged|closed)', content, re.IGNORECASE)),
        }
    
    def _categorize_problem(self, problem_text: str) -> str:
        """Categorize a problem by keywords."""
        problem_lower = problem_text.lower()
        
        if any(word in problem_lower for word in ['build', 'compile', 'webpack', 'vite']):
            return 'build_errors'
        elif any(word in problem_lower for word in ['test', 'spec', 'vitest', 'jest']):
            return 'test_failures'
        elif any(word in problem_lower for word in ['ci', 'github action', 'workflow']):
            return 'ci_cd_issues'
        elif any(word in problem_lower for word in ['pr', 'pull request', 'template']):
            return 'pr_template_issues'
        elif any(word in problem_lower for word in ['merge', 'conflict', 'rebase']):
            return 'merge_conflicts'
        elif any(word in problem_lower for word in ['dependency', 'package', 'npm', 'pip']):
            return 'dependencies'
        else:
            return 'other'
    
    def _categorize_command(self, command: str) -> str:
        """Categorize a command by its first word."""
        cmd_lower = command.lower()
        
        if cmd_lower.startswith(('git ', 'gh ')):
            return 'git'
        elif cmd_lower.startswith('gh '):
            return 'github_cli'
        elif any(cmd_lower.startswith(cmd) for cmd in ['npm ', 'npx ', 'yarn ', 'pnpm ']):
            return 'build'
        elif 'test' in cmd_lower or 'vitest' in cmd_lower or 'pytest' in cmd_lower:
            return 'test'
        elif any(cmd_lower.startswith(cmd) for cmd in ['curl ', 'wget ', './scripts/']):
            return 'validation'
        else:
            return 'other'
    
    def _get_section_content(self, content: str, start_pos: int, max_lines: int = 50) -> str:
        """Get content of a section starting at position."""
        lines = content[start_pos:].split('\n')
        section_lines = []
        
        for i, line in enumerate(lines):
            if i > 0 and line.startswith('##'):  # Next section
                break
            section_lines.append(line)
            if i >= max_lines:
                break
        
        return '\n'.join(section_lines)
    
    def _extract_time_from_section(self, section: str) -> int:
        """Extract time spent from a section (in minutes)."""
        time_pattern = r'(\d+(?:\.\d+)?)\s*(hour|hr|h|minute|min|m)'
        matches = re.finditer(time_pattern, section, re.IGNORECASE)
        
        total_minutes = 0
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            if unit in ['hour', 'hr', 'h']:
                total_minutes += value * 60
            else:
                total_minutes += value
        
        return int(total_minutes)
    
    def _update_workflow_patterns(self, learnings: Dict):
        """Update workflow patterns knowledge base."""
        kb_file = self.kb_dir / "workflow_patterns.json"
        with open(kb_file) as f:
            kb = json.load(f)
        
        kb['issues'].append({
            "issue_num": learnings['issue_num'],
            "phases": learnings['workflow_phases'],
            "total_time_hours": learnings['time_metrics']['actual_hours'],
            "files_changed": learnings['files_changed']
        })
        
        kb['last_updated'] = datetime.now().isoformat()
        
        with open(kb_file, 'w') as f:
            json.dump(kb, f, indent=2)
        
        print(f"   ✅ Updated workflow_patterns.json ({len(kb['issues'])} issues)")
    
    def _update_problem_solutions(self, learnings: Dict):
        """Update problem solutions knowledge base."""
        kb_file = self.kb_dir / "problem_solutions.json"
        with open(kb_file) as f:
            kb = json.load(f)
        
        # Add new problems (avoid duplicates)
        existing_problems = {p['problem'] for p in kb['problems']}
        new_count = 0
        
        for problem in learnings['problems_solved']:
            if problem['problem'] not in existing_problems:
                kb['problems'].append({
                    **problem,
                    "first_seen_issue": learnings['issue_num'],
                    "occurrences": 1
                })
                
                # Add to category
                category = problem['category']
                if category in kb['categories']:
                    kb['categories'][category].append(problem['problem'])
                
                new_count += 1
                existing_problems.add(problem['problem'])
            else:
                # Increment occurrence count
                for p in kb['problems']:
                    if p['problem'] == problem['problem']:
                        p['occurrences'] = p.get('occurrences', 1) + 1
        
        kb['last_updated'] = datetime.now().isoformat()
        
        with open(kb_file, 'w') as f:
            json.dump(kb, f, indent=2)
        
        print(f"   ✅ Updated problem_solutions.json (+{new_count} new problems, {len(kb['problems'])} total)")
    
    def _update_time_estimates(self, learnings: Dict):
        """Update time estimates knowledge base."""
        kb_file = self.kb_dir / "time_estimates.json"
        with open(kb_file) as f:
            kb = json.load(f)
        
        kb['completed_issues'].append({
            "issue_num": learnings['issue_num'],
            "estimated_hours": learnings['time_metrics']['estimated_hours'],
            "actual_hours": learnings['time_metrics']['actual_hours'],
            "multiplier": learnings['time_metrics']['multiplier']
        })
        
        # Recalculate statistics
        if len(kb['completed_issues']) > 0:
            multipliers = [issue['multiplier'] for issue in kb['completed_issues'] if issue['multiplier'] > 0]
            
            if multipliers:
                kb['statistics']['avg_multiplier'] = statistics.mean(multipliers)
                kb['statistics']['median_multiplier'] = statistics.median(multipliers)
                kb['statistics']['std_deviation'] = statistics.stdev(multipliers) if len(multipliers) > 1 else 0.0
                kb['statistics']['sample_size'] = len(multipliers)
        
        kb['last_updated'] = datetime.now().isoformat()
        
        with open(kb_file, 'w') as f:
            json.dump(kb, f, indent=2)
        
        print(f"   ✅ Updated time_estimates.json (avg multiplier: {kb['statistics']['avg_multiplier']:.3f})")
    
    def _update_command_sequences(self, learnings: Dict):
        """Update command sequences knowledge base."""
        kb_file = self.kb_dir / "command_sequences.json"
        with open(kb_file) as f:
            kb = json.load(f)
        
        # Add commands by category
        for cmd in learnings['command_sequences']:
            category = cmd['category']
            if category in kb['reusable_commands']:
                if cmd['command'] not in kb['reusable_commands'][category]:
                    kb['reusable_commands'][category].append(cmd['command'])
        
        kb['last_updated'] = datetime.now().isoformat()
        
        with open(kb_file, 'w') as f:
            json.dump(kb, f, indent=2)
        
        print(f"   ✅ Updated command_sequences.json")
    
    def _update_agent_metrics(self, learnings: Dict):
        """Update agent performance metrics."""
        kb_file = self.kb_dir / "agent_metrics.json"
        with open(kb_file) as f:
            kb = json.load(f)
        
        # Update workflow agent metrics
        agent = kb['agents']['workflow_agent']
        agent['trained_on_issues'] += 1
        agent['last_updated'] = datetime.now().isoformat()
        
        # Update knowledge base status
        kb['knowledge_base_status']['workflow_patterns_count'] = agent['trained_on_issues']
        
        # Load problem count
        with open(self.kb_dir / "problem_solutions.json") as f:
            problems = json.load(f)
            kb['knowledge_base_status']['problem_solutions_count'] = len(problems['problems'])
        
        # Determine confidence level
        issue_count = agent['trained_on_issues']
        if issue_count == 0:
            kb['knowledge_base_status']['confidence_level'] = 'none'
        elif issue_count < 5:
            kb['knowledge_base_status']['confidence_level'] = 'low'
        elif issue_count < 10:
            kb['knowledge_base_status']['confidence_level'] = 'medium'
        elif issue_count < 20:
            kb['knowledge_base_status']['confidence_level'] = 'high'
        else:
            kb['knowledge_base_status']['confidence_level'] = 'very_high'
            kb['knowledge_base_status']['ready_for_production'] = True
        
        with open(kb_file, 'w') as f:
            json.dump(kb, f, indent=2)
        
        print(f"   ✅ Updated agent_metrics.json (confidence: {kb['knowledge_base_status']['confidence_level']})")


def main():
    parser = argparse.ArgumentParser(
        description='Extract structured learnings from chat exports',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--export', type=str, required=True,
                        help='Path to chat export file')
    parser.add_argument('--kb-dir', type=str, default='agents/knowledge',
                        help='Knowledge base directory')
    parser.add_argument('--no-merge', action='store_true',
                        help='Extract only, do not merge into knowledge base')
    
    args = parser.parse_args()
    
    export_file = Path(args.export)
    if not export_file.exists():
        print(f"❌ Export file not found: {export_file}")
        sys.exit(1)
    
    extractor = LearningsExtractor(knowledge_base_dir=Path(args.kb_dir))
    
    # Extract learnings
    learnings = extractor.extract_from_export(export_file)
    
    if not learnings:
        print("❌ Failed to extract learnings")
        sys.exit(1)
    
    # Merge into knowledge base
    if not args.no_merge:
        extractor.merge_into_knowledge_base(learnings)
    
    print(f"\n✅ Learnings extraction complete")
    print(f"\nNext step:")
    print(f"  ./scripts/train_agent.py --issue {learnings['issue_num']}")


if __name__ == '__main__':
    main()
