"""
JMESPathMapMiddleware for box agent system.

Automatically generates JMESPath structure maps for large JSON tool results.
"""

import json
import logging
from typing import Callable, Any
from datetime import datetime, UTC
from langchain.tools.tool_node import ToolCallRequest
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from rapid_ai.agents.tools.trss_tools import get_tool

logger = logging.getLogger(__name__)

# Constants for file data formatting
MAX_LINE_LENGTH = 2000


def create_file_data(content: str, created_at: str | None = None, tool_call_id: str | None = None) -> dict[str, Any]:
    """Create a FileData object with timestamps and optional tool_call_id.
    
    Args:
        content: File content as string
        created_at: Optional creation timestamp (ISO format)
        tool_call_id: Optional tool call ID that created this file
    
    Returns:
        FileData dict with content, timestamps, and optional tool_call_id
    """
    lines = content.split("\n") if isinstance(content, str) else content
    lines = [line[i:i+MAX_LINE_LENGTH] for line in lines for i in range(0, len(line) or 1, MAX_LINE_LENGTH)]
    now = datetime.now(UTC).isoformat()
    
    result = {
        "content": lines,
        "created_at": created_at or now,
        "modified_at": now,
    }
    
    # Add tool_call_id if provided
    if tool_call_id:
        result["tool_call_id"] = tool_call_id
    
    return result


class JMESPathMapMiddleware(AgentMiddleware):
    """
    Middleware to automatically generate JMESPath structure maps for large JSON tool results.
    
    This middleware wraps tool calls and:
    1. Calls the handler (which includes FilesystemMiddleware)
    2. Detects when FilesystemMiddleware has saved a large tool result
    3. Loads and parses the JSON content from state files
    4. Generates a JMESPath structure map using view_jmespath_map tool
    5. Saves the map to a new file for easy reference
    6. Enhances the ToolMessage with information about both files
    """
    
    name = "jmespath_map"
    
    def __init__(self):
        """Initialize the middleware and load the view_jmespath_map tool."""
        super().__init__()
        # Load the tool function (not the LangChain tool wrapper)
        self.view_jmespath_map_tool = get_tool('view_jmespath_map', 'langchain')
    
    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        """
        Wrap tool calls to generate JMESPath maps for large JSON results.
        
        Args:
            request: ToolCallRequest with tool call info and runtime
            handler: The default handler that executes the tool (includes FilesystemMiddleware)
            
        Returns:
            ToolMessage or Command with enhanced information about JMESPath maps
        """
        tool_call = request.tool_call
        tool_call_id = tool_call['id']
        tool_name = tool_call['name']  # Capture original tool name
        
        # IMPORTANT: Skip processing for filesystem tools (grep, read_file, write_file, etc.)
        # These tools should not be wrapped as they don't return large JSON that needs JMESPath maps
        # More importantly, grep needs to access the original files without interference
        filesystem_tools = {'grep', 'read_file', 'write_file', 'append_file', 'list_dir'}
        if tool_name in filesystem_tools:
            return await handler(request)
        
        try:
            # Call the handler (FilesystemMiddleware runs before us)
            result = await handler(request)
            
            # Get current state to check for files
            state = request.state
            files = state.get("files", {})
            
            # Process based on result type
            if isinstance(result, Command):
                return self._process_command_result(result, tool_call_id, files, tool_name)
            elif isinstance(result, ToolMessage):
                return self._process_tool_message(result, tool_call_id, files, tool_name)
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in JMESPathMapMiddleware for tool {tool_call['name']}: {e}", exc_info=True)
            # Return the original result on error
            return await handler(request)
    
    def _process_command_result(self, result: Command, tool_call_id: str, files: dict, tool_name: str) -> Command:
        """Process a Command result and enhance messages with JMESPath map info."""
        update = result.update
        if update is None:
            return result
        
        message_updates = update.get("messages", [])
        file_updates = update.get("files", {})
        
        # Merge files from update with existing state files
        all_files = {**files, **file_updates}
        
        edited_message_updates = []
        additional_files = {}
        
        for message in message_updates:
            if isinstance(message, ToolMessage):
                enhanced_message, new_files = self._enhance_tool_message(
                    message, all_files, tool_name
                )
                edited_message_updates.append(enhanced_message)
                # Only add NEW files (JMESPath maps), never modify existing ones
                additional_files.update(new_files)
            else:
                edited_message_updates.append(message)
        
        # Return modified Command with enhanced messages and additional files
        # IMPORTANT: Only include file_updates (from FilesystemMiddleware) and additional_files (JMESPath maps)
        # Never include modified versions of existing files - this ensures grep can search original content
        return Command(update={
            **update,
            "messages": edited_message_updates,
            "files": {**file_updates, **additional_files}
        })
    
    def _process_tool_message(self, result: ToolMessage, tool_call_id: str, files: dict, tool_name: str) -> ToolMessage:
        """Process a ToolMessage result and enhance with JMESPath map info."""
        enhanced_message, new_files = self._enhance_tool_message(result, files, tool_name)
        
        # Note: We can't directly add files to state from here in a ToolMessage return
        # Files would need to be added via Command. If FilesystemMiddleware didn't
        # return a Command, there's no large file to process anyway.
        return enhanced_message
    
    def _enhance_tool_message(
        self, message: ToolMessage, files: dict, original_tool_name: str
    ) -> tuple[ToolMessage, dict[str, Any]]:
        """
        Enhance a ToolMessage with JMESPath map information if applicable.
        
        Args:
            message: The ToolMessage to enhance
            files: Dictionary of files in state
            original_tool_name: The name of the original tool that was called
        
        Returns:
            Tuple of (enhanced_message, new_files_dict)
        """
        tool_call_id = message.tool_call_id
        large_result_path = f"/large_tool_results/{tool_call_id}"
        
        # Check if this tool result was saved by FilesystemMiddleware
        if large_result_path not in files:
            return message, {}
        
        # Get file data and extract content
        file_data = files[large_result_path]
        content_lines = file_data.get("content", [])
        
        # Validate content format
        if not content_lines or not isinstance(content_lines[0], str):
            logger.error(f"Invalid file content format at {large_result_path}")
            return message, {}
        
        # Join the lines back together WITHOUT adding newlines
        # The content was split into chunks of MAX_LINE_LENGTH, not actual lines
        full_content = "".join(content_lines)
        
        # Calculate statistics for original file
        num_lines = len(content_lines)
        total_chars = sum(len(line) for line in content_lines)
        avg_chars = int(total_chars / num_lines) if num_lines > 0 else 0
        
        # Try to parse as JSON and generate JMESPath map
        jmespath_map_content = None
        map_stats = None
        
        try:
            # Parse the JSON content
            json_data = json.loads(full_content)
            
            # Generate JMESPath map using the tool function
            map_result = self.view_jmespath_map_tool.invoke({"json_blob": json_data})
            
            # Convert result to string format
            if isinstance(map_result, str):
                jmespath_map_content = map_result
            elif isinstance(map_result, dict):
                jmespath_map_content = json.dumps(map_result, indent=2)
            else:
                jmespath_map_content = str(map_result)
            
            # Calculate statistics for map file
            map_lines = jmespath_map_content.split("\n")
            map_num_lines = len(map_lines)
            map_total_chars = sum(len(line) for line in map_lines)
            map_avg_chars = int(map_total_chars / map_num_lines) if map_num_lines > 0 else 0
            
            map_stats = {
                "num_lines": map_num_lines,
                "avg_chars": map_avg_chars,
                "total_chars": map_total_chars
            }
            
        except json.JSONDecodeError:
            # Content is not JSON, skip map generation
            pass
        except Exception as e:
            logger.error(f"Error generating JMESPath map: {e}")
        
        # Create enhanced message if JMESPath map was generated
        if jmespath_map_content and map_stats:
            jmespath_map_path = f"/jmespath_maps/{tool_call_id}"
            jmespath_map_file = create_file_data(jmespath_map_content, tool_call_id=tool_call_id)
            
            # Use the original tool name that was passed in
            tool_name = original_tool_name
            
            # Create enhanced message with both file references including original tool name
            enhanced_content = f"""=== Tool: {tool_name} ===

!! ATTENTION !!
You MUST use the grep AND read_file tools to inspect the data from this tool.
It is too large to display here directly. This is NOT a summary of the data.


We saved the original result here: {large_result_path}
Statistics: {num_lines} lines, avg {avg_chars} chars/line

And a JMESPath structure map of the result here: {jmespath_map_path}
Map Statistics: {map_stats['num_lines']} lines, avg {map_stats['avg_chars']} chars/line


Use read_file tool to read the map for:
- Understanding the overall structure of the JSON data
- Finding paths to specific data fields
- Answering aggregate questions like "how many X are there?"
- Planning which parts of the large file to read
IMPORTANT: Always retrieve the FULL JMESPath map (no offset/limit needed since it's small - only {map_stats['num_lines']} lines).
{jmespath_map_path}


Use grep and read_file tools to read the original file for:
- Accessing specific keywords, names, IDs, etc...
- Reading detailed content
- Use offset/limit to read in chunks (it has {num_lines} lines)
{large_result_path}


## Tool Result Inpsection Examples:

1. **View the JMESPath structure map** (shows data organization):
   read_file(path="{jmespath_map_path}")

2. **Search for specific data** (e.g., find "Sudan"):
   grep(pattern="keyword", path="/large_tool_results", glob="{tool_call_id}", output_mode="content")

3. **Count instances of a keyword**:
   grep(pattern="keyword", path="/large_tool_results", glob="{tool_call_id}", output_mode="count")

3. **Read sections of the original data**:
   read_file(path="{large_result_path}", offset=0, limit=200)"""
            
            enhanced_message = ToolMessage(
                content=enhanced_content,
                name=tool_name,
                tool_call_id=tool_call_id
            )
            
            return enhanced_message, {jmespath_map_path: jmespath_map_file}
        else:
            # Keep original message if JMESPath generation failed
            return message, {}
