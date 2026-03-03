#!/usr/bin/env python3
"""
Record Issue Completion - Learn from completed issues

This script records completion data for an issue and updates the knowledge base.

Usage:
    ./scripts/record-completion.py <issue_number> <actual_hours> [notes]
    
Example:
    ./scripts/record-completion.py 24 7.0 "Tests took longer than expected"
"""

import sys
from pathlib import Path

# Add parent directory to path to import next-issue module
sys.path.insert(0, str(Path(__file__).parent))

from next_issue import IssueKnowledge, IssueSelector, TRACKING_FILE, KNOWLEDGE_FILE


def main():
    if len(sys.argv) < 3:
        print("Usage: ./scripts/record-completion.py <issue_number> <actual_hours> [notes]")
        print("\nExample:")
        print("  ./scripts/record-completion.py 24 7.0 'Tests took longer than expected'")
        return 1
    
    try:
        issue_number = int(sys.argv[1])
        actual_hours = float(sys.argv[2])
        notes = sys.argv[3] if len(sys.argv) > 3 else ""
    except ValueError:
        print("❌ Error: Issue number must be integer, actual hours must be float")
        return 1
    
    # Load knowledge
    knowledge = IssueKnowledge(KNOWLEDGE_FILE)
    
    # Get issue details from tracking file
    selector = IssueSelector(TRACKING_FILE, knowledge)
    issue = next((i for i in selector.issues if i["number"] == issue_number), None)
    
    if not issue:
        print(f"❌ Error: Issue #{issue_number} not found in tracking file")
        return 1
    
    # Record completion
    estimated_hours = issue["estimated_hours"]
    knowledge.record_completion(issue_number, estimated_hours, actual_hours, notes)
    
    # Calculate variance
    variance = actual_hours - estimated_hours
    variance_pct = (variance / estimated_hours * 100) if estimated_hours > 0 else 0
    
    print("=" * 80)
    print("ISSUE COMPLETION RECORDED")
    print("=" * 80)
    print(f"\n✅ Issue #{issue_number} completion data saved")
    print(f"\n📊 Statistics:")
    print(f"   • Estimated time: {estimated_hours:.1f} hours")
    print(f"   • Actual time: {actual_hours:.1f} hours")
    print(f"   • Variance: {variance:+.1f} hours ({variance_pct:+.1f}%)")
    print(f"   • Multiplier: {actual_hours/estimated_hours:.2f}x")
    
    if notes:
        print(f"\n📝 Notes: {notes}")
    
    # Show updated patterns
    avg_mult = knowledge.data["patterns"]["avg_time_multiplier"]
    total_completed = len(knowledge.data["completed_issues"])
    
    print(f"\n💡 Updated Learning:")
    print(f"   • Total completed issues: {total_completed}")
    print(f"   • Average time multiplier: {avg_mult:.2f}x")
    print(f"   • Future estimates will be adjusted by: {avg_mult:.2f}x")
    
    # Suggest pattern learning
    if abs(variance_pct) > 50:
        print(f"\n⚠️  Significant variance detected!")
        if variance_pct > 0:
            suggestion = f"Issue took {variance_pct:.0f}% longer than estimated"
            print(f"   Consider: Why did this take longer?")
            print(f"   • Was the scope larger than expected?")
            print(f"   • Were there unexpected technical challenges?")
            print(f"   • Did testing reveal issues requiring fixes?")
        else:
            suggestion = f"Issue completed {abs(variance_pct):.0f}% faster than estimated"
            print(f"   Consider: Why was this faster?")
            print(f"   • Was the estimate too conservative?")
            print(f"   • Were there reusable patterns from previous work?")
            print(f"   • Was the scope clearer than expected?")
    
    print("\n" + "=" * 80)
    print("\nKnowledge base updated: .issue-resolution-knowledge.json")
    print("This data will improve future time estimates.")
    print("\n💡 Tip: Add insights to tracking plan's 'Lessons Learned' section")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
