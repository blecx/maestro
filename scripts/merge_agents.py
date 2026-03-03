import os
import glob

prompts_dir = '.github/prompts/agents'
agents_dir = '.github/agents'

for prompt_file in glob.glob(f"{prompts_dir}/*.md"):
    filename = os.path.basename(prompt_file)
    if filename == "README.md":
        continue
    
    agent_name = filename.replace('-dev', '')
    target_agent_file = os.path.join(agents_dir, agent_name)
    
    if os.path.exists(target_agent_file):
        with open(prompt_file, 'r') as f:
            lines = f.readlines()
        
        # Remove the main title if it exists
        if lines and lines[0].startswith('# Agent:'):
            lines = lines[1:]
        while lines and lines[0].strip() == '':
            lines.pop(0)
            
        content_to_append = "".join(lines)
        
        with open(target_agent_file, 'a') as f:
            f.write("\n\n## Extended Workflow Execution Guidelines\n")
            f.write("*(Imported from legacy prompts directory)*\n\n")
            f.write(content_to_append)
        print(f"Merged {filename} into {agent_name}")
    else:
        print(f"Target {target_agent_file} not found for {filename}! Moving it.")
        os.rename(prompt_file, target_agent_file)
