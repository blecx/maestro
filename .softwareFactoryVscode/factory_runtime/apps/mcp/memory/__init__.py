"""mcp-memory: Knowledge graph MCP server for long-term agent memory.

Provides three memory layers:
- Short-term: recent issue context (last 10 runs)
- Long-term: lessons learned per issue (persists forever)
- Knowledge graph: entity relationships (file ↔ domain ↔ issue)

This package-owned service persists reusable lessons and relationships.
"""
