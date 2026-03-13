import glob
import os

DISCLAIMER = "\n> **Note**: This documentation describes runtime execution code. It is **not** the source of workflow policy. For workflow policy authority, see `.copilot/skills/resolve-issue-workflow/SKILL.md`.\n"

docs = glob.glob("docs/maestro/agents/*.md") + ["agents/README.md"]

for doc in docs:
    with open(doc, 'r') as f:
        content = f.read()
    
    if "source of workflow policy" in content.lower():
        continue
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i+1, DISCLAIMER)
            break
            
    with open(doc, 'w') as f:
        f.write('\n'.join(lines))
