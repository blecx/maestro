# Maestro Trunc Learnings

## Makefile Generation via LLMs
When deploying or modifying Makefiles programmatically (especially via `cat << EOF` in Bash through Copilot/AI environments), **hard tabs (`\t`) are frequently converted into spaces**. 

Since Makefiles strictly require hard tabs for indented execution blocks, this causes `*** Fehlt Trenner. Schluss.` (Missing separator) crashes. 

**Resolution:** 
When generating a Makefile via autonomous agent or AI bash execution, use Python's file descriptor write with explicit `\t` characters to enforce strict tab indentation instead of relying on Bash heredocs:

```python
with open("Makefile", "w") as f:
    f.write("target:\n\t@echo \"Hello World\"\n")
```
