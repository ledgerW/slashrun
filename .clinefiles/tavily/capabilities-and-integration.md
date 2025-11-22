# Tavily Web Search Capabilities & Integration

**When to read this guide:** Adding web search, content extraction, website crawling, or real-time web data capabilities to your application.

## Overview

Tavily is a search engine optimized for LLMs and AI agents, providing real-time web information. This template uses **two Tavily MCP servers** to provide comprehensive web search capabilities:

1. **Tavily Expert** (SSE) - Hosted server with built-in documentation and guidance tools
2. **github.com/tavily-ai/tavily-mcp** (Local) - Direct access to core Tavily APIs

## Core Capabilities

### 1. **Search** (`tavily-search`)
Real-time web search with AI-powered results.

**Key Features:**
- **Search Depth**: `basic` (1 credit) or `advanced` (10 credits)
- **Topics**: `general` or `news` (with time filtering)
- **Time Filters**: `day`, `week`, `month`, `year`, or custom date ranges
- **Domain Control**: Include/exclude specific domains
- **Result Options**: Include images, raw HTML content, answers

**Common Use Cases:**
- Current events and news monitoring
- Market research and competitive intelligence
- Technical documentation searches
- Academic research with domain filtering
- Product comparison and reviews

### 2. **Extract** (`tavily-extract`)
Extract structured content from specific URLs.

**Key Features:**
- **Extract Depth**: `basic` (1 credit per 5 URLs) or `advanced` (2 credits per 5 URLs)
- **Batch Processing**: Extract multiple URLs in one request
- **Image Support**: Optionally include images from pages
- **Format Options**: Markdown or plain text output

**Common Use Cases:**
- Content analysis from known URLs
- Extracting documentation pages
- Gathering data from multiple sources
- LinkedIn profile data (use `advanced` depth)
- Processing search results for deeper analysis

**Best Practice:** Two-step process - search first to find relevant URLs, then extract from high-scoring results only.

### 3. **Crawl** (`tavily-crawl`)
Systematically explore websites starting from a base URL.

**Key Features:**
- **Depth Control**: How far from base URL to explore
- **Breadth Control**: Links to follow per page
- **Total Limit**: Maximum links to process
- **Path Selection**: Regex patterns for URL filtering
- **Domain Filtering**: Restrict to specific domains/subdomains
- **Natural Language Instructions**: Guide what pages to return

**Common Use Cases:**
- Documentation site exploration
- Website content audits
- Discovering related pages
- Building knowledge bases from websites
- Analyzing site structure and organization

### 4. **Map** (`tavily-map`)
Create structured maps of website URLs and navigation.

**Key Features:**
- Same control parameters as crawl
- Returns URL structure without content
- Lightweight for site discovery
- Useful for understanding website architecture

**Common Use Cases:**
- Site structure analysis
- Content discovery and planning
- Navigation path mapping
- SEO and site audit preparation

## MCP Servers Configuration

This template uses **both** Tavily MCP servers, each with specific advantages:

### Tavily Expert (SSE Server)
**Server Name:** `Tavily Expert`  
**Type:** SSE (Server-Sent Events)  
**URL:** `https://tavily.api.tadata.com/mcp/tavily/[your-workspace-id]`

**Provides:**
- All core tools (search, extract, crawl, map)
- Documentation tools (API docs, best practices, integration guides)
- LangChain integration guidance
- Built-in examples and patterns

**When to Use:**
- Need documentation or guidance on Tavily usage
- Want best practices and optimization tips
- Building LangChain integrations
- Learning Tavily capabilities

### github.com/tavily-ai/tavily-mcp (Local Installation)
**Server Name:** `github.com/tavily-ai/tavily-mcp`  
**Type:** stdio (Local Node.js process)  
**Location:** `/Users/ledger/Documents/Cline/MCP/github.com/tavily-ai/tavily-mcp`

**Provides:**
- Direct access to core Tavily tools
- Local installation and control
- No dependency on remote server
- Consistent with other local MCP servers

**When to Use:**
- Production implementations
- Need guaranteed availability
- Prefer local installations
- Want to customize or extend functionality

## LangChain Integration

**⚠️ IMPORTANT:** Use `langchain-tavily` package, NOT `langchain_community.tools.tavily_search` (deprecated).

### Installation
```bash
# In langchain_/ directory
uv add langchain-tavily
```

### TavilySearch
```python
from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=5,
    topic="general",  # or "news"
    search_depth="basic",  # or "advanced"
    include_answer=True,
    include_raw_content=False,
    include_images=False
)

# Use in agent
result = tool.invoke({"query": "latest AI developments"})
```

### TavilyExtract
```python
from langchain_tavily import TavilyExtract

tool = TavilyExtract(
    extract_depth="basic",  # or "advanced" for LinkedIn, complex pages
    include_images=False
)

# Extract from URLs
result = tool.invoke({
    "urls": ["https://example.com/article"]
})
```

### Agent Integration
```python
from langchain_tavily import TavilySearch, TavilyExtract
from langchain.agents import create_openai_tools_agent, AgentExecutor

# Initialize tools
tavily_search = TavilySearch(max_results=5)
tavily_extract = TavilyExtract()

# Add to agent tools
tools = [tavily_search, tavily_extract, ...other_tools]

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(agent=agent, tools=tools)
```

## When to Use Tavily

### ✅ Good Use Cases

**Real-Time Information Needs:**
- Current events, news, market data
- Recently published content
- Time-sensitive information
- Live web data

**Research and Analysis:**
- Competitive intelligence
- Market research
- Academic research with domain filtering
- Technical documentation searches

**Content Discovery:**
- Finding relevant sources
- Website exploration
- Documentation aggregation
- Knowledge base building

**Verification and Fact-Checking:**
- Cross-referencing information
- Source validation
- Current status verification

### ❌ When NOT to Use Tavily

**Historical/Static Data:**
- Use retrieval from your own database or vector store
- Pre-indexed documentation
- Historical records

**High-Volume Operations:**
- Batch processing with API limits
- Real-time chat without caching
- Operations where cost is critical

**Private/Internal Data:**
- Internal documentation
- Private databases
- Proprietary information

## Best Practices

### Search Optimization

1. **Be Specific**: Use contextual terms, not generic queries
   - Good: "Python asyncio best practices 2025"
   - Bad: "Python programming"

2. **Use Domain Filtering**: Focus on trusted sources
   ```python
   tool = TavilySearch(
       include_domains=["nature.com", "arxiv.org", "ieee.org"],
       max_results=5
   )
   ```

3. **Choose Right Depth**:
   - `basic`: Quick searches, general information (1 credit)
   - `advanced`: Comprehensive research, critical decisions (10 credits)

4. **Time Filtering**: Use for news/current events
   ```python
   tool = TavilySearch(
       topic="news",
       days=3,  # Last 3 days
       max_results=10
   )
   ```

### Extract Optimization

1. **Two-Step Process**: Search first, extract later
   ```python
   # Step 1: Search
   search_results = search_tool.invoke({"query": "Python async patterns"})
   
   # Step 2: Filter by relevance score, then extract
   high_score_urls = [r['url'] for r in search_results if r['score'] > 0.5]
   content = extract_tool.invoke({"urls": high_score_urls})
   ```

2. **Use Advanced for Complex Pages**:
   - LinkedIn profiles
   - Pages with tables/structured data
   - Dynamic content pages

3. **Batch Multiple URLs**: Process up to 5 URLs per credit

### Crawl Guidelines

1. **Start Narrow**: Begin with low depth/breadth
   ```python
   # Test configuration
   crawl_tool.invoke({
       "url": "https://docs.example.com",
       "max_depth": 1,
       "max_breadth": 10,
       "limit": 20
   })
   ```

2. **Use Instructions**: Guide the crawler naturally
   ```python
   crawl_tool.invoke({
       "url": "https://docs.example.com",
       "instructions": "Focus on API reference and getting started guides"
   })
   ```

3. **Filter Paths**: Use regex for specific sections
   ```python
   crawl_tool.invoke({
       "url": "https://docs.example.com",
       "select_paths": ["/docs/.*", "/api/.*"],
       "exclude_domains": ["^support\.example\.com$"]
   })
   ```

## Credit Usage

**Free Tier:** 1,000 credits/month (no credit card required)

**Cost by Operation:**
- **Search Basic**: 1 credit
- **Search Advanced**: 10 credits
- **Extract Basic**: 1 credit per 5 URLs
- **Extract Advanced**: 2 credits per 5 URLs
- **Crawl/Map**: Varies by depth and breadth

**Optimization Tips:**
- Use basic depth for development/testing
- Cache results when possible
- Filter before extracting
- Start with small crawls

## Common Patterns

### Pattern 1: Research Assistant
```python
from langchain_tavily import TavilySearch

# Search for recent information
search_tool = TavilySearch(
    topic="news",
    days=7,
    max_results=10,
    include_answer=True
)

# Use in agent for research tasks
```

### Pattern 2: Documentation Aggregator
```python
from langchain_tavily import TavilySearch, TavilyExtract

# 1. Find relevant documentation
search_results = search_tool.invoke({
    "query": "Python FastAPI best practices",
    "include_domains": ["fastapi.tiangolo.com", "realpython.com"]
})

# 2. Extract full content
urls = [r['url'] for r in search_results]
content = extract_tool.invoke({"urls": urls})
```

### Pattern 3: Competitive Intelligence
```python
# Monitor competitor announcements
search_tool = TavilySearch(
    topic="news",
    days=1,
    include_domains=["techcrunch.com", "venturebeat.com"],
    exclude_domains=["pinterest.com", "quora.com"]
)
```

### Pattern 4: Website Knowledge Base
```python
# Crawl documentation site
from langchain_tavily import TavilyCrawl

crawl_results = crawl_tool.invoke({
    "url": "https://docs.product.com",
    "max_depth": 2,
    "max_breadth": 20,
    "limit": 50,
    "instructions": "Focus on API documentation and tutorials",
    "select_paths": ["/docs/.*", "/tutorials/.*"]
})
```

## Integration with This Template

### In LangChain Agents

Use Tavily tools in your middleware-centric agent architecture:

```python
# In langchain_/src/middleware/tools_middleware.py
from langchain_tavily import TavilySearch, TavilyExtract

class ToolsMiddleware:
    def __init__(self):
        self.tools = [
            TavilySearch(max_results=5, topic="general"),
            TavilyExtract(extract_depth="basic"),
            # ... other tools
        ]
```

### With Next.js Frontend

Call agent with Tavily-enabled tools:

```typescript
// In nextjs_/components/agent-chat.tsx
const response = await fetch('/api/agent', {
  method: 'POST',
  body: JSON.stringify({
    message: "Search for latest React 19 features",
    thread_id: threadId
  })
});
```

The agent automatically uses Tavily when web search is needed.

## Troubleshooting

### "Rate limit exceeded"
- Check credit usage in Tavily dashboard
- Reduce max_results or search frequency
- Use basic depth during development

### "No results found"
- Query too specific or niche
- Try broader search terms
- Remove domain filters temporarily

### "Extraction failed"
- Try advanced depth for complex pages
- Verify URLs are publicly accessible
- Check if site blocks crawlers

### "Crawl incomplete"
- Increase limit parameter
- Adjust max_depth/max_breadth
- Check select_paths regex patterns

## Additional Resources

- **Get API Key**: https://app.tavily.com/home (free tier, no credit card)
- **API Documentation**: Use `tavily_get_api_docs_tool` from Tavily Expert MCP
- **Best Practices**: Use `tavily_get_search_best_practices_tool` or `tavily_get_extract_best_practices_tool`
- **LangChain Integration**: Use `tavily_get_langchain_integration_tool` for detailed examples
- **Official Docs**: https://docs.tavily.com

## Summary

Tavily provides essential web search capabilities for AI agents. Use it when you need:
- Real-time web information
- Current events and news
- Website content extraction
- Documentation aggregation
- Competitive intelligence

Choose the right tool (search/extract/crawl/map), optimize for cost (basic vs advanced), and integrate seamlessly with LangChain using the `langchain-tavily` package.
