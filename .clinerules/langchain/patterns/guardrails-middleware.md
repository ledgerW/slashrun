# Guardrails Middleware Pattern

**Create generalizable middleware for validation, safety checks, and output filtering**

---

## Overview

Guardrails middleware provides safety and validation layers around agent behavior. This pattern shows how to build **generalizable** middleware that accepts configuration parameters to enforce rules, validate outputs, and apply content filtering.

## Core Concept

Guardrails middleware should be:
- **Configurable** - Accept rules, prompts, and models as init parameters
- **Reusable** - Work across different agents and use cases
- **Composable** - Stack with other middleware
- **Transparent** - Log what was filtered or blocked

---

## Basic Guardrails Middleware

### Example: Content Safety Guardrails

```python
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ModelRequest, ModelResponse
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from typing import Literal, Optional

class SafetyViolation(BaseModel):
    """Structured output for safety analysis."""
    is_safe: bool = Field(description="Whether content is safe")
    violation_type: Optional[Literal["hate_speech", "violence", "adult_content", "pii", "none"]] = Field(
        description="Type of safety violation if any"
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Severity of violation"
    )
    explanation: str = Field(description="Why content was flagged")

class ContentSafetyMiddleware(AgentMiddleware):
    """Generalizable middleware for content safety validation.
    
    Can be configured with custom guidance, rules, and structured output model.
    Uses before/after model hooks to validate inputs and outputs.
    """
    
    def __init__(
        self,
        *,
        system_prompt_guidance: str = None,
        safety_rules: list[str] = None,
        validation_model: str = "anthropic:claude-4-5-haiku-20251029",
        block_violations: bool = True,
        severity_threshold: Literal["low", "medium", "high", "critical"] = "high"
    ):
        """Initialize safety guardrails with configurable parameters.
        
        Args:
            system_prompt_guidance: Instructions added to system prompt about content safety
            safety_rules: List of specific safety rules to enforce
            validation_model: LLM model to use for safety analysis
            block_violations: Whether to block unsafe content or just log warnings
            severity_threshold: Minimum severity to trigger blocking
        """
        super().__init__()
        
        # Default system prompt guidance
        self.system_prompt_guidance = system_prompt_guidance or """
## Content Safety Guidelines

You must follow these safety guidelines:
- Do not generate harmful, offensive, or inappropriate content
- Respect user privacy and do not share personal information
- Avoid generating content that could be used for malicious purposes
- If asked to do something unsafe, politely decline and explain why

These are CRITICAL requirements - violations will result in blocking your output.
"""
        
        # Default safety rules
        self.safety_rules = safety_rules or [
            "No hate speech or discriminatory content",
            "No graphic violence or gore",
            "No adult or sexually explicit content",
            "No personally identifiable information (PII) exposure",
            "No instructions for illegal activities"
        ]
        
        self.block_violations = block_violations
        self.severity_threshold = severity_threshold
        
        # Initialize validation LLM with structured output
        validator_llm = ChatAnthropic(
            model=validation_model,
            temperature=0.0
        )
        self.validator = validator_llm.with_structured_output(SafetyViolation)
    
    def wrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Inject safety guidance into system prompt (before model call)."""
        # Add safety guidance to system prompt
        safety_context = self.system_prompt_guidance
        
        # Add specific rules
        safety_context += "\n\n### Specific Safety Rules\n"
        for i, rule in enumerate(self.safety_rules, 1):
            safety_context += f"{i}. {rule}\n"
        
        request.system_prompt = (
            request.system_prompt + safety_context
            if request.system_prompt
            else safety_context
        )
        
        # Call model
        response = handler(request)
        
        # Validate output (after model call)
        if response.message and response.message.content:
            validation = self._validate_content(response.message.content)
            
            if not validation.is_safe:
                if self._should_block(validation):
                    # Block the response
                    response.message.content = self._create_blocked_message(validation)
                else:
                    # Log warning but allow
                    print(f"[GUARDRAILS WARNING] {validation.violation_type}: {validation.explanation}")
        
        return response
    
    async def awrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Inject safety guidance into system prompt (async version)."""
        # Add safety guidance to system prompt
        safety_context = self.system_prompt_guidance
        
        # Add specific rules
        safety_context += "\n\n### Specific Safety Rules\n"
        for i, rule in enumerate(self.safety_rules, 1):
            safety_context += f"{i}. {rule}\n"
        
        request.system_prompt = (
            request.system_prompt + safety_context
            if request.system_prompt
            else safety_context
        )
        
        # Call model
        response = await handler(request)
        
        # Validate output (after model call)
        if response.message and response.message.content:
            validation = await self._avalidate_content(response.message.content)
            
            if not validation.is_safe:
                if self._should_block(validation):
                    # Block the response
                    response.message.content = self._create_blocked_message(validation)
                else:
                    # Log warning but allow
                    print(f"[GUARDRAILS WARNING] {validation.violation_type}: {validation.explanation}")
        
        return response
    
    def _validate_content(self, content: str) -> SafetyViolation:
        """Validate content using LLM with structured output."""
        validation_prompt = f"""Analyze this content for safety violations:

Content: {content}

Safety Rules:
{chr(10).join(f"- {rule}" for rule in self.safety_rules)}

Determine if the content violates any safety rules."""
        
        result = self.validator.invoke(validation_prompt)
        return result
    
    async def _avalidate_content(self, content: str) -> SafetyViolation:
        """Validate content using LLM with structured output (async)."""
        validation_prompt = f"""Analyze this content for safety violations:

Content: {content}

Safety Rules:
{chr(10).join(f"- {rule}" for rule in self.safety_rules)}

Determine if the content violates any safety rules."""
        
        result = await self.validator.ainvoke(validation_prompt)
        return result
    
    def _should_block(self, validation: SafetyViolation) -> bool:
        """Determine if content should be blocked based on severity threshold."""
        if not self.block_violations:
            return False
        
        severity_order = ["low", "medium", "high", "critical"]
        threshold_index = severity_order.index(self.severity_threshold)
        violation_index = severity_order.index(validation.severity)
        
        return violation_index >= threshold_index
    
    def _create_blocked_message(self, validation: SafetyViolation) -> str:
        """Create message explaining why content was blocked."""
        return f"""I apologize, but I cannot provide that response as it violates content safety guidelines.

Violation Type: {validation.violation_type}
Severity: {validation.severity}
Reason: {validation.explanation}

Please rephrase your request in a way that adheres to safety guidelines."""
```

---

## Usage Examples

### Example 1: Basic Safety (Default Rules)

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[web_search, calculator],
    middleware=[
        ContentSafetyMiddleware()  # Use defaults
    ],
    system_prompt="You are a helpful assistant."
)
```

### Example 2: Custom Rules (Enterprise Use Case)

```python
# Enterprise-specific safety rules
enterprise_rules = [
    "No disclosure of proprietary company information",
    "No financial advice or investment recommendations",
    "No medical diagnoses or treatment recommendations",
    "No legal advice or contract interpretation",
    "No personal data of customers or employees"
]

enterprise_guidance = """
## Enterprise Safety Policy

You are operating in an enterprise environment with strict compliance requirements.

CRITICAL: You must never:
1. Share proprietary business information
2. Provide financial, medical, or legal advice
3. Expose customer or employee personal data
4. Make commitments on behalf of the company

If asked about sensitive topics, redirect to appropriate channels.
"""

agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[crm_query, document_search],
    middleware=[
        ContentSafetyMiddleware(
            system_prompt_guidance=enterprise_guidance,
            safety_rules=enterprise_rules,
            block_violations=True,
            severity_threshold="medium"  # Stricter threshold
        )
    ],
    system_prompt="You are an enterprise assistant."
)
```

### Example 3: PII Detection & Redaction

```python
class PIIRedaction(BaseModel):
    """Structured output for PII detection."""
    contains_pii: bool
    pii_types: list[Literal["email", "phone", "ssn", "credit_card", "address"]]
    redacted_content: str = Field(description="Content with PII replaced by [REDACTED]")

class PIIGuardrailsMiddleware(AgentMiddleware):
    """Detect and redact personally identifiable information."""
    
    def __init__(
        self,
        *,
        system_prompt_guidance: str = None,
        redaction_model: str = "anthropic:claude-4-5-haiku-20251029",
        auto_redact: bool = True
    ):
        super().__init__()
        
        self.system_prompt_guidance = system_prompt_guidance or """
## PII Protection

You must NEVER include personally identifiable information (PII) in your responses:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Physical addresses
- Full names with additional identifying info

If you need to reference such information, use placeholders like [EMAIL], [PHONE], etc.
"""
        
        self.auto_redact = auto_redact
        
        redactor_llm = ChatAnthropic(model=redaction_model, temperature=0.0)
        self.redactor = redactor_llm.with_structured_output(PIIRedaction)
    
    def wrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Inject PII guidance and validate output."""
        # Add PII guidance to system prompt
        request.system_prompt = (
            request.system_prompt + self.system_prompt_guidance
            if request.system_prompt
            else self.system_prompt_guidance
        )
        
        # Call model
        response = handler(request)
        
        # Check for PII in output
        if response.message and response.message.content and self.auto_redact:
            analysis = self._analyze_pii(response.message.content)
            
            if analysis.contains_pii:
                print(f"[PII DETECTED] Found: {', '.join(analysis.pii_types)}")
                response.message.content = analysis.redacted_content
        
        return response
    
    async def awrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Inject PII guidance and validate output (async)."""
        # Add PII guidance to system prompt
        request.system_prompt = (
            request.system_prompt + self.system_prompt_guidance
            if request.system_prompt
            else self.system_prompt_guidance
        )
        
        # Call model
        response = await handler(request)
        
        # Check for PII in output
        if response.message and response.message.content and self.auto_redact:
            analysis = await self._aanalyze_pii(response.message.content)
            
            if analysis.contains_pii:
                print(f"[PII DETECTED] Found: {', '.join(analysis.pii_types)}")
                response.message.content = analysis.redacted_content
        
        return response
    
    def _analyze_pii(self, content: str) -> PIIRedaction:
        """Detect and redact PII using LLM."""
        prompt = f"""Analyze this content for PII and redact if found:

Content: {content}

Detect: emails, phone numbers, SSN, credit cards, physical addresses.
Return the content with any PII replaced by [REDACTED]."""
        
        return self.redactor.invoke(prompt)
    
    async def _aanalyze_pii(self, content: str) -> PIIRedaction:
        """Detect and redact PII using LLM (async)."""
        prompt = f"""Analyze this content for PII and redact if found:

Content: {content}

Detect: emails, phone numbers, SSN, credit cards, physical addresses.
Return the content with any PII replaced by [REDACTED]."""
        
        return await self.redactor.ainvoke(prompt)

# Usage
agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[customer_search, order_lookup],
    middleware=[
        PIIGuardrailsMiddleware(
            auto_redact=True  # Automatically redact detected PII
        )
    ],
    system_prompt="You are a customer service assistant."
)
```

---

## Advanced Patterns

### Pattern 1: Multi-Stage Validation

```python
class MultiStageGuardrailsMiddleware(AgentMiddleware):
    """Apply multiple validation stages with different severity levels."""
    
    def __init__(
        self,
        *,
        stages: list[dict]  # Each stage has rules, threshold, model
    ):
        super().__init__()
        self.stages = stages
        
        # Initialize validators for each stage
        self.validators = []
        for stage in stages:
            llm = ChatAnthropic(model=stage["model"], temperature=0.0)
            validator = llm.with_structured_output(SafetyViolation)
            self.validators.append({
                "validator": validator,
                "rules": stage["rules"],
                "threshold": stage["threshold"],
                "stage_name": stage["name"]
            })
    
    def wrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Apply multi-stage validation."""
        response = handler(request)
        
        if response.message and response.message.content:
            # Apply each validation stage
            for stage in self.validators:
                validation = self._validate_stage(
                    response.message.content,
                    stage["validator"],
                    stage["rules"]
                )
                
                if not validation.is_safe:
                    print(f"[{stage['stage_name']}] Violation detected: {validation.violation_type}")
                    
                    if self._exceeds_threshold(validation.severity, stage["threshold"]):
                        response.message.content = f"Content blocked by {stage['stage_name']}"
                        break
        
        return response

# Usage: Progressive validation stages
agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[
        MultiStageGuardrailsMiddleware(
            stages=[
                {
                    "name": "Content Safety",
                    "model": "anthropic:claude-4-5-haiku-20251029",
                    "rules": ["No hate speech", "No violence"],
                    "threshold": "high"
                },
                {
                    "name": "PII Detection",
                    "model": "anthropic:claude-4-5-haiku-20251029",
                    "rules": ["No PII exposure"],
                    "threshold": "medium"
                },
                {
                    "name": "Compliance Check",
                    "model": "anthropic:claude-4-5-haiku-20251029",
                    "rules": ["No financial advice", "No medical advice"],
                    "threshold": "low"
                }
            ]
        )
    ]
)
```

### Pattern 2: Domain-Specific Guardrails

```python
class DomainGuardrailsMiddleware(AgentMiddleware):
    """Guardrails tailored to specific domains (medical, legal, financial)."""
    
    def __init__(
        self,
        *,
        domain: Literal["medical", "legal", "financial"],
        custom_rules: list[str] = None
    ):
        super().__init__()
        self.domain = domain
        
        # Domain-specific rule sets
        domain_rules = {
            "medical": [
                "No medical diagnoses or treatment recommendations",
                "Always recommend consulting healthcare professionals",
                "No prescription medication advice",
                "Clearly state you're not a medical professional"
            ],
            "legal": [
                "No legal advice or interpretations",
                "Always recommend consulting licensed attorneys",
                "No contract or document drafting",
                "Clearly state you're not a lawyer"
            ],
            "financial": [
                "No investment advice or recommendations",
                "Always recommend consulting financial advisors",
                "No specific stock or crypto recommendations",
                "Clearly state you're not a financial advisor"
            ]
        }
        
        self.rules = custom_rules or domain_rules[domain]
        
        # Domain-specific guidance
        self.guidance = self._generate_domain_guidance()
        
        # Validator
        llm = ChatAnthropic(model="anthropic:claude-4-5-haiku-20251029", temperature=0.0)
        self.validator = llm.with_structured_output(SafetyViolation)
    
    def _generate_domain_guidance(self) -> str:
        """Generate domain-specific system prompt guidance."""
        return f"""
## {self.domain.title()} Domain Guardrails

You are operating in the {self.domain} domain. CRITICAL RULES:

{chr(10).join(f"- {rule}" for rule in self.rules)}

If users ask for {self.domain} advice:
1. Politely decline
2. Explain you cannot provide {self.domain} advice
3. Recommend they consult qualified professionals
4. Offer general information only (if appropriate)
"""

# Usage
medical_agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[
        DomainGuardrailsMiddleware(
            domain="medical"
        )
    ],
    system_prompt="You are a health information assistant."
)
```

### Pattern 3: Configurable Output Formatting

```python
class OutputFormattingGuardrailsMiddleware(AgentMiddleware):
    """Enforce output format requirements with structured output validation."""
    
    def __init__(
        self,
        *,
        format_requirements: str,
        output_model: type[BaseModel],
        validator_model: str = "anthropic:claude-4-5-haiku-20251029",
        auto_reformat: bool = True
    ):
        """Initialize with format requirements and structured output model.
        
        Args:
            format_requirements: Description of required output format
            output_model: Pydantic model defining the expected structure
            validator_model: LLM to use for validation and reformatting
            auto_reformat: Whether to automatically reformat non-compliant outputs
        """
        super().__init__()
        self.format_requirements = format_requirements
        self.output_model = output_model
        self.auto_reformat = auto_reformat
        
        formatter_llm = ChatAnthropic(model=validator_model, temperature=0.0)
        self.formatter = formatter_llm.with_structured_output(output_model)
    
    def wrap_model_call(self, request: ModelRequest, handler) -> ModelResponse:
        """Inject format requirements and validate output format."""
        # Add format requirements to system prompt
        format_guidance = f"""
## Output Format Requirements

{self.format_requirements}

Your output MUST adhere to this format. Non-compliant outputs will be reformatted.
"""
        
        request.system_prompt = (
            request.system_prompt + format_guidance
            if request.system_prompt
            else format_guidance
        )
        
        # Call model
        response = handler(request)
        
        # Validate and reformat if needed
        if response.message and response.message.content and self.auto_reformat:
            try:
                # Try to parse as structured output
                structured = self.formatter.invoke(response.message.content)
                # Convert back to formatted string
                response.message.content = structured.model_dump_json(indent=2)
            except Exception as e:
                print(f"[FORMAT ERROR] Could not enforce format: {e}")
        
        return response

# Example usage with report format
class ReportFormat(BaseModel):
    """Structured report format."""
    executive_summary: str
    key_findings: list[str]
    recommendations: list[str]
    conclusion: str

agent = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[
        OutputFormattingGuardrailsMiddleware(
            format_requirements="""All responses must be structured reports with:
- Executive summary (2-3 sentences)
- Key findings (bullet points)
- Recommendations (actionable items)
- Conclusion (1-2 sentences)""",
            output_model=ReportFormat,
            auto_reformat=True
        )
    ],
    system_prompt="You are a business analyst."
)
```

---

## Key Principles

### 1. Make Middleware Generalizable

✅ **Good**: Configurable with init parameters
```python
def __init__(
    self,
    *,
    system_prompt_guidance: str = None,
    safety_rules: list[str] = None,
    validation_model: str = "...",
    block_violations: bool = True
):
```

❌ **Bad**: Hardcoded values
```python
def __init__(self):
    self.rules = ["No hate speech"]  # Not configurable
    self.model = "gpt-4"  # Hardcoded
```

### 2. Use Structured Output for Validation

✅ **Good**: Type-safe structured output
```python
class SafetyViolation(BaseModel):
    is_safe: bool
    violation_type: Optional[str]
    severity: Literal["low", "medium", "high", "critical"]
    explanation: str

validator = llm.with_structured_output(SafetyViolation)
```

❌ **Bad**: Parsing text responses
```python
response = llm.invoke("Is this safe? Answer yes or no")
is_safe = "yes" in response.lower()  # Fragile
```

### 3. Support Both Before and After Hooks

```python
def wrap_model_call(self, request, handler):
    # BEFORE: Inject guidance into system prompt
    request.system_prompt = request.system_prompt + self.guidance
    
    # DURING: Call model
    response = handler(request)
    
    # AFTER: Validate and potentially block output
    if not self._is_safe(response):
        response.message.content = "[BLOCKED]"
    
    return response
```

### 4. Provide Both Sync and Async Versions

```python
def wrap_model_call(self, request, handler):
    """Sync version."""
    # Implementation
    
async def awrap_model_call(self, request, handler):
    """Async version - required for async agents."""
    # Same logic but with await
```

### 5. Log Violations for Monitoring

```python
if not validation.is_safe:
    # Log violation for monitoring
    print(f"[GUARDRAILS] {validation.violation_type}: {validation.explanation}")
    
    # Optionally send to logging service
    logger.warning(
        "Safety violation detected",
        extra={
            "violation_type": validation.violation_type,
            "severity": validation.severity,
            "user_id": request.context.get("user_id")
        }
    )
```

---

## Testing Guardrails

```python
# Test that safety guidance is injected
def test_safety_guidance_injection():
    middleware = ContentSafetyMiddleware()
    request = ModelRequest(system_prompt="Base prompt")
    
    # Wrap call
    modified = middleware.wrap_model_call(request, lambda r: r)
    
    # Verify guidance was added
    assert "Content Safety Guidelines" in modified.system_prompt

# Test that unsafe content is blocked
async def test_content_blocking():
    middleware = ContentSafetyMiddleware(
        block_violations=True,
        severity_threshold="high"
    )
    
    # Mock unsafe response
    unsafe_response = ModelResponse(
        message=AIMessage(content="[Unsafe content here]")
    )
    
    # Should be blocked
    result = await middleware.awrap_model_call(
        request=ModelRequest(),
        handler=lambda r: unsafe_response
    )
    
    assert "cannot provide that response" in result.message.content

# Test configurability
def test_custom_rules():
    custom_rules = ["No custom violation", "No other violation"]
    middleware = ContentSafetyMiddleware(safety_rules=custom_rules)
    
    assert middleware.safety_rules == custom_rules
```

---

## Common Use Cases

1. **Content Safety** - Block harmful, offensive, or inappropriate content
2. **PII Protection** - Detect and redact personally identifiable information
3. **Domain Compliance** - Enforce medical/legal/financial advice restrictions
4. **Output Formatting** - Ensure responses match required structure
5. **Data Security** - Prevent exposure of sensitive business information
6. **Regulatory Compliance** - Meet industry-specific regulations (HIPAA, GDPR, etc.)

---

## Best Practices

1. **Use fast models for validation** - Haiku for quick safety checks
2. **Provide clear feedback** - Explain WHY content was blocked
3. **Make thresholds configurable** - Different use cases need different sensitivity
4. **Log all violations** - Monitor for patterns and false positives
5. **Test extensively** - Validate both blocking and allowing edge cases
6. **Stack multiple guardrails** - Layer different safety checks
7. **Provide escape hatches** - Allow administrators to override when needed

---

## Next Steps

- **Middleware Fundamentals**: See [middleware.md](../core/middleware.md)
- **Middleware-Centric Pattern**: See [middleware-centric.md](./middleware-centric.md)
- **Structured Output**: See [structured-output.md](../core/structured-output.md)

---

## Summary

Guardrails middleware provides configurable safety and validation layers that:
- Accept guidance, rules, and models as init parameters
- Use structured output for reliable validation
- Support both before-model and after-model hooks
- Enable monitoring and logging of violations
- Work across different agents and use cases

This is a **critical pattern** for production agents handling sensitive data or operating in regulated industries.
