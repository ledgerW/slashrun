# Model Update Guide - January 2025

## Latest Model Identifiers (as of January 2025)

### OpenAI Models

**GPT-5.1 (Latest - Released Late 2025)**
- Full model: `gpt-5.1` - Latest reasoning model with enhanced capabilities
- Supports reasoning parameters: `effort` (low/medium/high) and `summary` (auto/concise/detailed)
- Supports verbosity control: low/medium/high
- Uses Responses API for advanced reasoning

**GPT-5 (Released August 7, 2025)**
- Full model: `gpt-5`
- Fast variant: `gpt-5-mini`
- Lightweight: `gpt-5-nano`
- Chat variant: `gpt-5-chat`

**GPT-4.1 (Released April 14, 2025)**
- Full model: `gpt-4.1`
- Fast variant: `gpt-4.1-mini`
- Lightweight: `gpt-4.1-nano`

**GPT-4o (Legacy, still supported)**
- Full model: `gpt-4o`
- Fast variant: `gpt-4o-mini`

### Anthropic Claude Models

**Claude 4.5 (Current Generation - 2025)**
- Sonnet: `claude-sonnet-4-5-20250929` (September 29, 2025 snapshot)
- Haiku: `claude-haiku-4-5-20251001` (October 1, 2025 snapshot)

**Claude 4.1 Opus (Released August 5, 2025)**
- Opus: `claude-opus-4-1-20250805` (August 5, 2025 snapshot)

**Claude 4 (May 2025)**
- Opus: `claude-opus-4-20250514`
- Sonnet: `claude-sonnet-4-20250514`

**Claude 3.x (Legacy, still supported)**
- Sonnet 3.7: `claude-3-7-sonnet-20250219`
- Sonnet 3.5: `claude-3-5-sonnet-20241022`
- Haiku 3.5: `claude-3-5-haiku-20241022`

## Recommended Defaults

### For Production Applications
- **Primary**: `claude-sonnet-4-5-20250929` - Best balance of performance and cost
- **Fast/Cheap**: `claude-haiku-4-5-20251001` - For high-volume, simple tasks
- **Premium**: `claude-opus-4-1-20250805` - For complex reasoning

### For OpenAI Users
- **Primary**: `gpt-5.1` - Latest reasoning model with advanced capabilities
- **Standard**: `gpt-5` - Latest generation (non-reasoning)
- **Fast/Cheap**: `gpt-5-mini` - For high-volume tasks
- **Legacy**: `gpt-4.1` - If GPT-5 not available

## Migration Strategy

### From GPT-4o to Current Models
```python
# Old (2024)
model = ChatOpenAI(model="gpt-4o")

# New (2025) - Latest with reasoning
model = ChatOpenAI(
    model="gpt-5.1",
    reasoning={
        "effort": "medium",  # low/medium/high
        "summary": "auto"     # auto/concise/detailed
    },
    verbosity="medium"  # low/medium/high
)

# New (2025) - Standard
model = ChatOpenAI(model="gpt-5")

# New (2025) - Budget option
model = ChatOpenAI(model="gpt-5-mini")
```

### From Claude 3.5 to Current Models
```python
# Old (2024)
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# New (2025) - Recommended
model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

# New (2025) - Budget option
model = ChatAnthropic(model="claude-haiku-4-5-20251001")
```

## Provider-Specific Notes

### OpenAI
- GPT-5.1 is the latest reasoning model with enhanced capabilities
- Supports reasoning parameters for effort control and summary formatting
- Supports verbosity levels for controlling response detail
- Uses Responses API for advanced reasoning features
- GPT-5 is the default in ChatGPT for all users
- Legacy GPT-4 models no longer available via ChatGPT (except for Pro users)
- All variants support tool calling, structured outputs, and streaming

### Anthropic
- Claude 4.5 models available via API, AWS Bedrock, and GCP Vertex AI
- AWS Bedrock IDs use format: `anthropic.claude-sonnet-4-5-20250929-v1:0`
- GCP Vertex IDs use format: `claude-sonnet-4-5@20250929`
- All Claude 4+ models support extended thinking and priority tier

## Cost Considerations

### Claude Pricing (per million tokens)
- **Sonnet 4.5**: $3 input / $15 output
- **Haiku 4.5**: $1 input / $5 output
- **Opus 4.1**: $15 input / $75 output

### OpenAI Pricing
- Check [OpenAI pricing page](https://openai.com/api/pricing/) for current rates
- GPT-5 variants generally more expensive than GPT-4.1
- Consider using mini/nano variants for cost-sensitive applications

## References

- [Anthropic Models Overview](https://docs.claude.com/claude/docs/models-overview)
- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [LangChain Chat Models Integration](https://python.langchain.com/docs/integrations/chat/)
