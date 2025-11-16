# Service Interface Documentation

**Purpose**: Single source of truth for integration contracts between Next.js, LangChain agents, and Supabase.

## ⚠️ Critical Principle: Interface-First Development

**ALL integration points MUST be documented here BEFORE implementation.**

```
❌ WRONG: Implement → Document
✅ RIGHT: Document → Implement → Validate
```

### Workflow

1. **Design Phase**: Document interface contract (schemas, types, flow)
2. **Review Phase**: Stakeholder approval on contract (MUST freeze before coding)
3. **Implementation Phase**: Build according to frozen contract
4. **Validation Phase**: Verify implementation matches contract exactly

### Status Indicators

- 🔵 **PLANNED** - Contract designed, not yet implemented
- 🟢 **IMPLEMENTED** - Contract exists in running code
- 🔴 **DEPRECATED** - Being phased out

---

## Quick Navigation

### By Service Pair

- **[Next.js ↔ LangChain](./nextjs-langchain-interface.md)** - Frontend to agent communication
  - Agent invocation patterns
  - State and context schemas
  - Thread management
  - Streaming patterns

- **[Next.js ↔ Supabase](./nextjs-supabase-interface.md)** - Frontend to database
  - CRUD operations
  - Realtime subscriptions
  - RLS policies
  - Type definitions

- **[LangChain ↔ Supabase](./langchain-supabase-interface.md)** - Agent tools to database
  - Tool database operations
  - Service role access
  - Custom functions
  - Data contracts

### By Agent

All agents documented in their respective README.md files:

- [Nation Agent](../../langchain_/src/agents/nation_agent/README.md#interface-specifications)
- Organization Agent (coming soon)
- Individual Agent (coming soon)
- Population Agent (coming soon)

### By Feature

- Scenario Management: [Next.js ↔ Supabase](./nextjs-supabase-interface.md#scenarios)
- Actor Actions: [Next.js ↔ LangChain](./nextjs-langchain-interface.md#nation-agent)
- Timestep Processing: All three interface docs
- Chat/Messaging: [Next.js ↔ LangChain](./nextjs-langchain-interface.md#streaming)

---

## When to Update These Documents

### Adding New Agent

**BEFORE any code:**
1. Create agent README with interface specifications
2. Add contract to `nextjs-langchain-interface.md`
3. Add tool operations to `langchain-supabase-interface.md`
4. Mark all as 🔵 PLANNED
5. Get stakeholder approval
6. Implement according to specs
7. Mark as 🟢 IMPLEMENTED

### Adding New Endpoint

**BEFORE any code:**
1. Design endpoint contract (inputs, outputs, errors)
2. Update relevant interface document
3. Reference agent or database operations
4. Mark as 🔵 PLANNED
5. Implement according to contract
6. Validate implementation matches
7. Mark as 🟢 IMPLEMENTED

### Database Schema Changes

**BEFORE migration:**
1. Update interface docs showing new schema
2. Update affected agent tool contracts
3. Update affected endpoint contracts
4. Implement migration
5. Validate all contracts still valid

### Modifying Existing Integration

**ALWAYS:**
1. Update interface doc FIRST (not after)
2. Mark changes clearly
3. Update all related contracts
4. Implement changes
5. Validate against updated contract

---

## Validation Checklist

Use this before marking any contract as 🟢 IMPLEMENTED:

### Agent Implementation
- [ ] Agent README has complete State schema (TypedDict)
- [ ] Agent README has complete Context schema (dataclass)
- [ ] Agent README shows expected outputs
- [ ] Python schemas exactly match what code uses
- [ ] Integration points referenced

### Next.js Implementation
- [ ] TypeScript types match Python schemas
- [ ] useStream() pattern used correctly
- [ ] Context passed via options (not config.configurable)
- [ ] Thread management follows patterns
- [ ] Endpoint documented in interface doc

### Database Operations
- [ ] All tables/functions used are documented
- [ ] RLS policies noted
- [ ] Service role vs user role clarified
- [ ] Migration files referenced

### Cross-Service Validation
- [ ] Bidirectional references work (endpoint → agent → database)
- [ ] No conflicting sources of truth
- [ ] All integration points documented
- [ ] Status indicators accurate

---

## Design Templates

### Agent Interface Specification Template

See example in [nation_agent README](../../langchain_/src/agents/nation_agent/README.md#interface-specifications)

Required sections:
- State Schema (TypedDict)
- Context Schema (dataclass)
- Output Structure
- Example Invocation
- Integration Points

### Endpoint Contract Template

```markdown
## [Endpoint Name]

### Status
🔵 PLANNED | 🟢 IMPLEMENTED

### Agent/Operation
[Link to agent README or database doc]

### Request
\`\`\`typescript
// TypeScript types
\`\`\`

### Response
\`\`\`typescript
// TypeScript types
\`\`\`

### Invocation Pattern
\`\`\`typescript
// Code example
\`\`\`

### State & Context
\`\`\`python
# Python schemas (link to agent README)
\`\`\`

### Error Handling
- Possible errors
- How to handle

### References
- Migration files
- Related endpoints
- Documentation links
```

---

## Consequences of Violating Interface-First Principle

**If you implement before documenting:**

1. ❌ **Multiple sources of truth** - Code and docs diverge
2. ❌ **Integration failures** - Teams build incompatible interfaces
3. ❌ **Hard to validate** - No spec to test against
4. ❌ **Difficult onboarding** - New developers can't understand system
5. ❌ **Brittle changes** - Small changes break unexpectedly

**Follow the workflow. Always document first.**

---

## FAQ

**Q: Do I really need to document EVERYTHING?**
A: Yes. Any place where Next.js talks to LangChain, Next.js talks to Supabase, or LangChain talks to Supabase needs a contract.

**Q: What if I'm just doing a quick prototype?**
A: Document it. Even prototypes need integration contracts. It takes 5 minutes and saves hours of debugging.

**Q: The interface doc seems redundant with my code.**
A: That's the point. The doc is the spec, the code is the implementation. They should match exactly.

**Q: Can I update the interface doc after implementing?**
A: Only if you're documenting EXISTING legacy code (like we're doing with nation_agent). For new work: document FIRST.

**Q: What if requirements change during implementation?**
A: Update the interface doc, get approval, then update code. Always keep contract as source of truth.

---

Last Updated: 2025-01-16
