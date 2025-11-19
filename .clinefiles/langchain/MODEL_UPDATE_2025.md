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

## ⚠️ CRITICAL: GPT-5 Parameter Changes

**GPT-5 family models DO NOT support the `temperature` parameter.**

All GPT-5 models (`gpt-5`, `gpt-5.1`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-chat`) use different parameters:

- **`reasoning_effort`** (GPT-5.1 only): Controls reasoning depth
  - Values: `"low"`, `"medium"`, `"high"`
  - Used for models with advanced reasoning capabilities

- **`verbosity`**: Controls response detail level (all GPT-5 models)
  - Values: `"low"`, `"medium"`, `"high"`
  - Use this for behavior similar to `temperature` control

**GPT-4.x and Claude models still support `temperature` as normal.**

## Migration Strategy

### From GPT-4o to Current Models
```python
# ❌ Old (2024) - with temperature
model = ChatOpenAI(model="gpt-4o", temperature=0.7)

# ✅ New (2025) - GPT-5.1 with reasoning (NO temperature)
model = ChatOpenAI(
    model="gpt-5.1",
    reasoning_effort="medium",  # low/medium/high - controls reasoning depth
    verbosity="medium"          # low/medium/high - controls response detail
)

# ✅ New (2025) - Standard GPT-5 (NO temperature)
model = ChatOpenAI(
    model="gpt-5",
    verbosity="medium"  # Use verbosity instead of temperature
)

# ✅ New (2025) - Budget option (NO temperature)
model = ChatOpenAI(
    model="gpt-5-mini",
    verbosity="low"  # Use verbosity for response control
)

# ✅ GPT-4.1 still supports temperature
model = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7  # temperature still works for GPT-4.x
)
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

**⚠️ Parameter Compatibility:**
- **GPT-5 family** (`gpt-5`, `gpt-5.1`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-chat`):
  - ❌ Does NOT support `temperature`
  - ✅ Use `reasoning_effort` (GPT-5.1 only) and `verbosity` instead
- **GPT-4 family** (`gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`):
  - ✅ Still supports `temperature` parameter

**Model Features:**
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
