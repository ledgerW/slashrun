"""
Default filesystem middleware system prompt.

This prompt provides guidance on using filesystem tools for large data exploration.
"""

default_filesystem_prompt = """
=== Filesystem Tools Available (Optional Utility) ===

**Available tools**:
- ls
- read_file (great for inspecting chunks of large files)
- grep      (great for searching for specific entities, IDs, keywords)
- glob (all paths start with `/`)

**Efficient Strategy for Large Files**:
When working with large tool results, a workflow like this might be effective:
1. **Overview**: Check `/jmespath_maps/{tool_call_id}` first to understand the data structure and fields available
2. **Search**: Use `grep` to find specific entities, IDs, or keywords from your task in `/large_tool_results/{tool_call_id}`
3. **Inspect**: Use `read_file` with the line numbers from grep hits to view the surrounding context

**Example grep usage** (search file contents):
- `grep(pattern="term", path="/", glob="*.json")` - Search all JSON files for "term"
- `grep(pattern="term", path="/large_tool_results", glob="{tool_call_id}")` - Search specific saved result file
- `grep(pattern="term", path="/", glob="*.txt", output_mode="content")` - Show matching lines with context
- `grep(pattern="term", path="/data", glob="**/*.json", output_mode="count")` - Count matches per file

Note: Both `path` (directory) and `glob` (file pattern) parameters are required.

**Example read_file usage** (read file contents):
- `read_file(path="/data/entities.json", offset=0, limit=250)` - Read first 250 lines of the file
- `read_file(path="/large_tool_results/call_xyz", offset=1234, limit=50)` - Read 50 lines starting at line 1234 (from grep hit)

**IMPORTANT: Tool Usage**:
⚠️ Be cautious about calling more than 2-3 filesystem tools at once. Too many simultaneous calls can overwhelm processing and lead to timeouts or errors. Call tools strategically and wait for results before proceeding.
"""
