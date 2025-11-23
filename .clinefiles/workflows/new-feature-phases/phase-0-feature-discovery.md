# Phase 0: Feature Discovery & Planning [MANDATORY]

**Purpose:** Thoroughly plan the feature before writing any code

**Prerequisites:**
- Get-started workflow Phases 0-9 complete
- SYSTEM_REFERENCE.md exists
- PROJECT_REQUIREMENTS.md exists
- All services running and stable

**Key Insight:** Spending time in planning prevents wasted development effort. A well-planned feature takes 1/3 the time to implement compared to figuring it out during coding.

---

## Overview

Phase 0 is the **planning phase** for new features. Before touching any code, you must:

1. **Understand the Request** - What does the user actually want?
2. **Review Existing System** - How does this fit into current architecture?
3. **Design the Solution** - What needs to change in each service?
4. **Document the Plan** - Create FEATURE_PLAN.md with complete specifications
5. **Get Approval** - Confirm plan before implementation

**Do not proceed to implementation phases without completing Phase 0.**

---

## Step 1: Gather Feature Requirements

### Clarify User Intent

Ask clarifying questions to understand:

**What:**
- What is the feature supposed to do?
- What problem does it solve?
- What does success look like?

**Who:**
- Who will use this feature?
- What user roles are involved?
- What permissions are needed?

**When:**
- When/how do users access this feature?
- What triggers the feature?
- Are there time-based aspects?

**Where:**
- Where in the UI does this appear?
- Which pages are involved?
- How do users navigate to it?

**Why:**
- Why is this feature valuable?
- What's the business/user value?
- What happens if we don't build it?

### Document User Stories

Create user stories in format:
```
As a [user type]
I want to [action]
So that [benefit]
```

**Example:**
```
As a project manager
I want to export my scenario data to CSV
So that I can analyze it in Excel
```

### List Acceptance Criteria

For each user story, define acceptance criteria:

**Example:**
- [ ] User can click "Export" button on scenarios list page
- [ ] CSV file downloads with all scenario fields
- [ ] Export includes related actors and timesteps
- [ ] File name format: `scenarios-export-YYYY-MM-DD.csv`
- [ ] Export respects RLS (only user's data)

---

## Step 2: Review Existing System Architecture

### Read System Documentation

**Review these files in order:**

1. **SYSTEM_REFERENCE.md**
   - Current architecture overview
   - Services and their responsibilities
   - Integration points
   - API endpoints
   - Database schema

2. **PROJECT_REQUIREMENTS.md**
   - Existing entities
   - Current features
   - Entity relationships
   - MVP scope

3. **INTEGRATION_CHECKLIST.md**
   - How services communicate
   - Authentication patterns
   - Data flow patterns

### Identify Existing Patterns

Look for similar features already implemented:

**Questions to answer:**
- Are there similar features in the app?
- How do they handle [specific aspect]?
- What components/patterns can be reused?
- What conventions should be followed?

**Example:**
```
Looking to add CSV export feature...

Similar patterns found:
- PDF export on reports page uses button + server action
- File downloads use Next.js API routes
- Existing pattern: User clicks button → API route generates file → Download starts

Reuse:
- Button component pattern from reports page
- Server action pattern for file generation
- Toast notifications for success/error
```

### Assess Impact on Each Service

**For each service, determine:**

**Database (Supabase):**
- [ ] New tables needed? (List them)
- [ ] New columns in existing tables? (List them)
- [ ] New relationships? (Describe them)
- [ ] RLS policy changes? (Describe them)
- [ ] Seed data changes? (Describe them)

**Frontend (Next.js):**
- [ ] New pages/routes? (List them)
- [ ] New components? (List them)
- [ ] Updated components? (List them)
- [ ] Form changes? (Describe them)
- [ ] Navigation changes? (Describe them)

**Agent Service (if applicable):**
- [ ] New tools needed? (List them)
- [ ] Web search/data extraction needed? → See `.clinefiles/tavily/capabilities-and-integration.md`
- [ ] Updated prompts? (Describe them)
- [ ] New middleware? (Describe them)
- [ ] Memory changes? (Describe them)
- [ ] Streaming changes? (Describe them)

---

## Step 3: Classify Feature Complexity

### Determine Feature Type

Based on service impact:

**Simple Feature** (1-2 days, Phases: 0, 2, 5)
- Single service impacted
- No database changes
- Uses existing components/patterns
- Minimal integration testing

**Moderate Feature** (3-5 days, Phases: 0, 1, 2, 4, 5 or 0, 3, 4, 5)
- 2 services impacted
- May include database changes
- Some new components/patterns
- Integration testing required

**Complex Feature** (1-2 weeks, Phases: 0, 1, 2, 3, 4, 5)
- All services impacted
- Multiple database changes
- New patterns/architectures
- Extensive integration testing

### Identify Required Phases

Based on classification:

| If Feature Needs... | Execute Phase |
|---------------------|---------------|
| Database table/column | Phase 1 |
| UI pages/components | Phase 2 |
| Agent tools/capabilities | Phase 3 |
| 2+ services touched | Phase 4 |
| Always required | Phase 0, 5 |

**Example:**
```
Feature: Add notification preferences
- Database: New preferences table → Phase 1
- Frontend: Settings form → Phase 2
- No agent changes → Skip Phase 3
- Multiple services → Phase 4
- Documentation → Phase 5

Required Phases: 0, 1, 2, 4, 5 (Moderate complexity)
```

---

## Step 4: Design Database Schema Changes (If Phase 1 Needed)

### For New Tables

**Design table structure:**

```sql
-- Template for planning
create table [table_name] (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users on delete cascade not null,
  
  -- Feature-specific fields
  [field_name] [data_type] [constraints],
  
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

**Document:**
- Table name
- All columns with types
- Foreign keys
- Indexes needed
- RLS policies required

### For Existing Table Updates

**Document:**
- Table being modified
- Columns to add
- Default values
- Migration strategy (can existing data handle this?)
- RLS policy updates needed

### Design Relationships

**For each relationship, document:**

**One-to-Many:**
- Parent table
- Child table
- Foreign key column
- On delete behavior (cascade, restrict, set null)

**Many-to-Many:**
- Entity A
- Entity B
- Junction table name
- Composite primary key
- Additional fields in junction

**Example:**
```markdown
## Database Changes

### New Table: notification_preferences
- id (bigint, PK, auto-increment)
- user_id (uuid, FK to auth.users, cascade delete)
- email_enabled (boolean, default true)
- push_enabled (boolean, default false)
- frequency (text, default 'immediate', check: immediate/daily/weekly)
- created_at (timestamptz)
- updated_at (timestamptz)

**Indexes:**
- user_id (for lookups)

**RLS Policies:**
- Users can select their own preferences
- Users can insert their own preferences
- Users can update their own preferences
- Users cannot delete (soft delete with flag instead)

### Relationship:
- profiles 1:1 notification_preferences (via user_id)
```

---

## Step 5: Design UI/UX (If Phase 2 Needed)

### Sketch Page Layouts

**For each new/modified page:**

**Page:** [Page Name] (`/dashboard/path/to/page`)

**Layout:**
```
┌─────────────────────────────────────┐
│ Page Header                         │
│ [Title]          [Action Buttons]   │
├─────────────────────────────────────┤
│                                     │
│ Main Content Area                   │
│ [Describe what goes here]           │
│                                     │
│ [Component 1]                       │
│ [Component 2]                       │
│                                     │
└─────────────────────────────────────┘
```

**Components Needed:**
- Component 1: [Description]
- Component 2: [Description]

**shadcn/ui Components to Use:**
- Button (for actions)
- Card (for content display)
- Form, Input (for data entry)
- etc.

### Design Forms

**For each form:**

**Form Name:** [Name]

**Fields:**
```typescript
{
  field_name: {
    type: "text" | "email" | "number" | "select" | "textarea" | etc,
    label: "Display Label",
    placeholder: "Placeholder text",
    validation: "required" | "email" | "min:X" | "max:X" | etc,
    default: "default value if any"
  },
  // ... more fields
}
```

**Validation Rules:**
- Field 1: Required, min 3 characters
- Field 2: Optional, valid email format
- etc.

**Submit Behavior:**
- What happens on submit?
- Success message/action?
- Error handling?
- Redirect after success?

### Design Navigation Updates

**If adding to sidebar:**
- Navigation group (e.g., "Settings", "Reports")
- Menu item label
- Icon to use
- Route path
- Access control (who can see it?)

---

## Step 6: Design Agent Changes (If Phase 3 Needed)

### Design New Tools

**For each new tool:**

**Tool Name:** `tool_name_here`

**Purpose:** [What does this tool do?]

**Parameters:**
```typescript
{
  param1: {
    type: string | number | boolean | etc,
    description: "What this parameter is for",
    required: true | false
  },
  // ... more parameters
}
```

**Returns:**
```typescript
{
  // What the tool returns
  result: string,
  metadata: object,
  // etc.
}
```

**Implementation Notes:**
- Does it need database access?
- Does it call external APIs?
- Does it need user context?
- Error handling approach?

### Design Prompt Updates

**If updating system message:**

**Current behavior:**
[Describe what agent currently does]

**New behavior:**
[Describe what agent should do with new feature]

**Prompt additions:**
```
Additional instructions to add:
- Instruction 1
- Instruction 2
```

### Design Middleware Needs

**If new middleware required:**

**Middleware name:** [Name]

**Purpose:** [What capability does this add?]

**Configuration:**
```python
middleware = MiddlewareClass(
    param1=value1,
    param2=value2
)
```

**Integration:**
- How does it interact with existing middleware?
- Execution order important?

---

## Step 7: Identify Integration Points

### Map Data Flow

**Document how data flows between services:**

```
User Action
    ↓
Frontend Component
    ↓
[API Route / Server Action]
    ↓
Database Query (via Supabase client)
    ↓
[Optional: Agent Service call]
    ↓
Response to Frontend
    ↓
UI Update
```

**For each integration point, document:**
- What triggers it?
- What data is sent?
- What format? (JSON, FormData, etc.)
- What's the response?
- How are errors handled?

### Identify Authentication Requirements

**For each integration point:**
- [ ] Requires user to be logged in?
- [ ] Needs user_id in context?
- [ ] RLS policies will filter data?
- [ ] Special permissions needed?

### Identify Testing Scenarios

**Integration tests to create:**
1. [Scenario 1]: User does X, system does Y
2. [Scenario 2]: Edge case - what if Z?
3. [Scenario 3]: Error case - what if fails?

---

## Step 8: Assess Risks and Challenges

### Technical Risks

**Identify potential issues:**

**Performance:**
- Will this create N+1 queries?
- Large data export concerns?
- Real-time update scalability?

**Security:**
- Data exposure risks?
- RLS policy gaps?
- Input validation needs?

**Compatibility:**
- Breaking changes to existing features?
- API version concerns?
- Browser compatibility?

### Mitigation Strategies

**For each risk, document:**
- Risk description
- Likelihood (Low/Medium/High)
- Impact (Low/Medium/High)
- Mitigation approach

**Example:**
```
Risk: Large CSV exports (1000+ records) may timeout
- Likelihood: Medium
- Impact: High (feature unusable for power users)
- Mitigation: 
  1. Implement pagination/batching
  2. Add progress indicator
  3. Consider background job for very large exports
```

---

## Step 9: Estimate Effort

### Break Down Tasks

**For each phase you'll execute:**

**Phase 1: Database (if needed)**
- Create migration file (30 min)
- Write migration SQL (1 hour)
- Add RLS policies (1 hour)
- Test migration (30 min)
- Update documentation (30 min)

**Phase 2: Frontend (if needed)**
- Create page component (2 hours)
- Create form component (3 hours)
- Add navigation (30 min)
- Style and polish (1 hour)
- Add loading/error states (1 hour)

**Phase 3: Agent (if needed)**
- Create tool (2 hours)
- Update prompts (1 hour)
- Test in Studio (1 hour)
- Integration with frontend (2 hours)

**Phase 4: Integration Testing**
- Write test scenarios (1 hour)
- Execute tests (2 hours)
- Fix issues found (2-4 hours)

**Phase 5: Documentation**
- Update SYSTEM_REFERENCE.md (1 hour)
- Update PROJECT_REQUIREMENTS.md (30 min)
- Write feature docs (1 hour)

### Total Estimate

**Calculate total time:**
- Phase 1: [X hours]
- Phase 2: [Y hours]
- Phase 3: [Z hours]
- Phase 4: [A hours]
- Phase 5: [B hours]

**Total: [Sum] hours = [X] days**

**Add 25% buffer for unexpected issues.**

**Complexity Classification:**
- 1-2 days = Simple
- 3-5 days = Moderate
- 1-2 weeks = Complex

---

## Step 10: Create FEATURE_PLAN.md

### Generate Complete Feature Plan

Create `FEATURE_PLAN.md` in project root:

```markdown
# Feature Plan: [Feature Name]

**Status:** Planning
**Created:** [Date]
**Complexity:** Simple | Moderate | Complex
**Estimated Effort:** [X] days
**Required Phases:** [List phase numbers]

---

## 1. Feature Overview

### Purpose
[What this feature does and why it's valuable]

### User Stories
1. As a [user], I want to [action], so that [benefit]
2. [Additional stories]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## 2. System Impact Analysis

### Services Affected
- [x] Database (Supabase)
- [x] Frontend (Next.js)
- [ ] Agent Service

### Existing Patterns to Follow
- [Pattern 1]: [Where it's used in codebase]
- [Pattern 2]: [Where it's used in codebase]

### New Patterns Introduced
- [Pattern 1]: [Why needed]
- [Or: None - using existing patterns only]

---

## 3. Database Changes (Phase 1)

### New Tables
[Table designs from Step 4, or "None"]

### Existing Table Updates
[Column additions, or "None"]

### Relationships
[Relationship descriptions, or "None"]

### RLS Policies
[Policy descriptions for each table]

### Migration Strategy
[How to handle existing data, if applicable]

---

## 4. Frontend Changes (Phase 2)

### New Pages
1. `/dashboard/path/to/page` - [Description]

### New Components
1. `ComponentName` - [Description, location]

### Updated Components
1. `ComponentName` - [What changes]

### Navigation Updates
- Add "[Menu Item]" to [Navigation Group]
- Icon: [Icon name]
- Route: [Path]

### Form Designs
[Form specifications from Step 5]

### UI Mockups
[ASCII mockups or descriptions from Step 5]

---

## 5. Agent Service Changes (Phase 3)

[If not applicable: "Not applicable - no agent changes needed"]

### New Tools
[Tool designs from Step 6]

### Prompt Updates
[Prompt change descriptions]

### Middleware Changes
[Middleware additions/updates]

---

## 6. Integration Points (Phase 4)

### Data Flow
[Data flow diagram from Step 7]

### Integration Tests
1. [Test scenario 1]
2. [Test scenario 2]
3. [Test scenario 3]

### Authentication
[Auth requirements from Step 7]

---

## 7. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | L/M/H | L/M/H | [Strategy] |
| [Risk 2] | L/M/H | L/M/H | [Strategy] |

---

## 8. Implementation Checklist

### Phase 0: Planning
- [x] Feature requirements documented
- [x] FEATURE_PLAN.md created
- [ ] Plan reviewed and approved

### Phase 1: Database (if applicable)
- [ ] Migration created
- [ ] RLS policies added
- [ ] Migration tested
- [ ] Documentation updated

### Phase 2: Frontend (if applicable)
- [ ] Pages created
- [ ] Components created
- [ ] Forms implemented
- [ ] Navigation updated
- [ ] Loading/error states added

### Phase 3: Agent (if applicable)
- [ ] Tools implemented
- [ ] Prompts updated
- [ ] Tested in Studio
- [ ] Integrated with frontend

### Phase 4: Integration Testing
- [ ] Integration tests executed
- [ ] All tests passing
- [ ] RLS policies verified
- [ ] Performance acceptable

### Phase 5: Documentation
- [ ] SYSTEM_REFERENCE.md updated
- [ ] PROJECT_REQUIREMENTS.md updated
- [ ] Feature documentation created
- [ ] Troubleshooting guide updated

---

## 9. Success Metrics

### How to Verify Success
- [ ] All acceptance criteria met
- [ ] Feature works as specified
- [ ] No existing features broken
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Documentation complete

### Future Enhancements
[Ideas for v2, if applicable]

---

**Next Steps:**
1. Review this plan with stakeholders
2. Get approval to proceed
3. Begin Phase 1 (or whichever phase is first)
```

---

## Step 11: Review and Approval

### Self-Review Checklist

Before proceeding to implementation:

**Requirements:**
- [ ] User stories clear and specific
- [ ] Acceptance criteria measurable
- [ ] All questions answered

**Architecture:**
- [ ] Reviewed SYSTEM_REFERENCE.md
- [ ] Reviewed PROJECT_REQUIREMENTS.md
- [ ] Existing patterns identified
- [ ] Integration points mapped

**Design:**
- [ ] Database schema designed (if needed)
- [ ] UI mockups created (if needed)
- [ ] Agent tools designed (if needed)
- [ ] All designs documented

**Planning:**
- [ ] Risks identified and mitigated
- [ ] Effort estimated reasonably
- [ ] Phases identified correctly
- [ ] FEATURE_PLAN.md complete

**Quality:**
- [ ] RLS policies planned for all new tables
- [ ] Loading states planned
- [ ] Error handling planned
- [ ] User feedback planned

### Get Stakeholder Approval

**Present FEATURE_PLAN.md to:**
- Product owner
- Technical lead
- Other stakeholders

**Confirm:**
- [ ] Requirements accurate
- [ ] Approach reasonable
- [ ] Effort estimate acceptable
- [ ] Risks understood

**Document approval:**
- Approved by: [Name]
- Date: [Date]
- Notes: [Any feedback or changes]

---

## Common Issues and Solutions

### Issue 1: Unclear Requirements

**Symptom:** Can't answer key questions about feature

**Solution:**
- Ask more clarifying questions
- Create simple mockups to validate understanding
- Break feature into smaller pieces if too complex

### Issue 2: Feature Too Complex

**Symptom:** Estimate exceeds 2 weeks

**Solution:**
- Break into multiple smaller features
- Implement MVP first, enhancements later
- Reconsider if feature is necessary

### Issue 3: Existing Pattern Unclear

**Symptom:** Can't find similar code in codebase

**Solution:**
- Read .clinerules guides for patterns
- Look at most recently added features
- Ask user to clarify expected approach

### Issue 4: Integration Concerns

**Symptom:** Worried about breaking existing features

**Solution:**
- List all affected integration points
- Plan comprehensive testing in Phase 4
- Consider feature flags for gradual rollout

---

## Phase 0 Completion Checklist

Before proceeding to implementation phases:

- [ ] User requirements clearly understood
- [ ] SYSTEM_REFERENCE.md reviewed thoroughly
- [ ] PROJECT_REQUIREMENTS.md reviewed
- [ ] Existing patterns identified and documented
- [ ] Feature complexity classified
- [ ] Required phases identified
- [ ] Database changes designed (if Phase 1 needed)
- [ ] UI changes designed (if Phase 2 needed)
- [ ] Agent changes designed (if Phase 3 needed)
- [ ] Integration points mapped
- [ ] Risks identified and mitigations planned
- [ ] Effort estimated reasonably
- [ ] FEATURE_PLAN.md created and complete
- [ ] FEATURE_PLAN.md reviewed and approved

**Cannot proceed without complete, approved FEATURE_PLAN.md**

---

## Next Phase

**Proceed to:** 
- If database changes needed: [Phase 1: Database Schema Updates](./phase-1-database-updates.md)
- If only frontend changes: [Phase 2: Frontend Implementation](./phase-2-frontend-implementation.md)
- If only agent changes: [Phase 3: Agent Service Integration](./phase-3-agent-integration.md)
- If only documentation: [Phase 5: Documentation Update](./phase-5-documentation-update.md)

**With:**
- Complete FEATURE_PLAN.md document
- Clear understanding of requirements
- Approved implementation approach
- Identified phases to execute
