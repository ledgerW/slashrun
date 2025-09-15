# Pydantic Patterns & Best Practices

## Version & Critical Rule

SlashRun uses **Pydantic v2** (see pyproject.toml). **ALWAYS use `.model_dump()`, NEVER `.dict()`**

## Core Patterns

### 1. Database JSON Field Handling
**Problem**: Database JSON columns store dicts, but APIs use Pydantic models.

**Solution**: Always serialize when storing, validate when loading.

```python
# ✅ Store: Pydantic → dict
db_agent.persona = agent_data.persona.model_dump()

# ✅ Load: dict → Pydantic (conditional)
if isinstance(db_agent.persona, dict):
    persona = AgentPersonaData.model_validate(db_agent.persona)
```

**Examples**: See `app/api/agents.py` create/update endpoints, `app/agents/base/factory.py` persona handling.

### 2. Model Updates Pattern
```python
# ✅ Handle mixed Pydantic/dict updates
for field, value in update_data.items():
    if hasattr(value, 'model_dump'):
        setattr(agent, field, value.model_dump())
    else:
        setattr(agent, field, value)
```

**Example**: See `app/api/agents.py` update_agent endpoint.

### 3. Conditional Model Validation
Always check type before accessing Pydantic attributes on database objects.

**Example**: See `app/agents/base/factory.py` persona data handling.

## Common Pitfalls to Avoid

1. **Wrong serialization method**: Using `.dict()` instead of `.model_dump()`
2. **Assuming database objects are Pydantic**: They're dicts after loading from JSON columns
3. **Missing serialization**: Storing Pydantic objects directly in JSON fields
4. **v1/v2 mixing**: Inconsistent API usage across codebase

## Quick Debugging

```bash
# Find v1 patterns to update
grep -r "\.dict()" app/
grep -r "\.parse_obj(" app/
```

## Migration Notes

- **v1 → v2**: `.dict()` → `.model_dump()`, `Config` → `model_config = ConfigDict(...)`
- **Test both paths**: Serialization (model → dict) and validation (dict → model)

**Memory Aid**: "Database stores dicts, API uses models, always serialize between them."
