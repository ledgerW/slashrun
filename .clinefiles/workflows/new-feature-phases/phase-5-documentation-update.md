# Phase 5: Documentation & System Update [MANDATORY]

**Purpose:** Update all system documentation to reflect the new feature

**Prerequisites:**
- All previous phases complete
- Feature fully implemented and tested
- FEATURE_PLAN.md exists
- FEATURE_TEST_RESULTS.md exists (if Phase 4 executed)

**Always execute:** Every feature requires documentation updates

---

## Overview

Phase 5 ensures the system documentation stays current:

1. **PROJECT_REQUIREMENTS.md** - Add feature to requirements
2. **SYSTEM_REFERENCE.md** - Update architecture docs
3. **DATABASE_SCHEMA.md** - Document schema changes
4. **README.md** - Update feature list
5. **Troubleshooting** - Add common issues
6. **Guide Index** - Update if new patterns

---

## Step 1: Update PROJECT_REQUIREMENTS.md

### Add Feature to Features Section

```markdown
## MVP Features

[Existing features...]

### [X]. [Feature Name]

**User Story:** As a [user type], I want to [action], so that [benefit]

**Description:** [What the feature does]

**Acceptance Criteria:**
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

**Implementation Status:** ✅ Complete
**Implemented:** [Date]
**Location:** 
- Frontend: `/dashboard/[feature path]`
- Database: `[table_names]`
- Agent: `[tool names]` (if applicable)
```

### Update Entities Section (If Phase 1)

```markdown
### [Entity Name]

**Category:** Primary | Junction | System-Generated | Configuration

**Description:** [What this entity represents]

**Fields:**
- field_name (type) - Description
- [...]

**Relationships:**
- Belongs to: [Parent entity]
- Has many: [Child entities]
- Related to: [Junction relationships]

**CRUD Status:** ✅ Complete
**RLS Policies:** ✅ Configured
**Seed Data:** ✅ Available
```

---

## Step 2: Update SYSTEM_REFERENCE.md

### Update Architecture Overview (If Applicable)

**If feature adds new services or changes architecture:**

```markdown
## Architecture Overview

[Update diagram or description to include new feature]
```

### Update Database Schema Section

**Add new tables:**

```markdown
#### [table_name]
- **Purpose:** [What this table stores]
- **User-scoped:** Yes/No
- **Relationships:** [Key relationships]
- **RLS:** Users can only access their own records
- **Indexes:** user_id, [other indexed fields]
```

### Update API Endpoints (If Applicable)

**If feature adds API routes:**

```markdown
### Feature Name Endpoints

#### GET /api/feature
**Description:** [What it does]
**Authentication:** Required
**Parameters:**
- param1 (type) - Description

**Response:**
```json
{
  "data": [...],
  "count": 10
}
```

**Example:**
```bash
curl http://localhost:3000/api/feature?param1=value
```
```

### Update Agent Service Section (If Phase 3)

**Add new tools:**

```markdown
### Feature Tools

#### tool_name
**Purpose:** [What the tool does]
**Parameters:**
- param1 (type) - Description

**Returns:**
```json
{
  "success": true,
  "result": "..."
}
```

**Usage in prompts:**
Use this tool when user asks about [scenario]
```

### Update Integration Points

**Document new integration:**

```markdown
### [Feature Name] Integration

**Data Flow:**
```
User Action
    ↓
[Frontend Component]
    ↓
[Database Query / Agent Call]
    ↓
Response
```

**Files Involved:**
- `app/dashboard/[feature]/page.tsx`
- `components/[feature]-form.tsx`
- `supabase/migrations/[timestamp]_[name].sql`
- `agent-service/tools/[feature]_tools.py` (if applicable)
```

### Update Common Development Workflows

**Add feature-specific workflow:**

```markdown
### Modifying [Feature Name]

**To add a field:**
1. Create migration: `supabase migration new add_field_to_feature`
2. Add column in migration
3. Update RLS policies if needed
4. Update form schema in component
5. Test CRUD operations

**To modify behavior:**
1. Update component: `components/[feature]-form.tsx`
2. Update validation schema
3. Test in browser
4. Update documentation
```

---

## Step 3: Update DATABASE_SCHEMA.md (If Phase 1)

### Add Complete Table Documentation

```markdown
### [table_name]
[Detailed description]

**Columns:**
- id (bigint, PK, auto-increment)
- user_id (uuid, FK to auth.users)
- [field_name] ([type], [constraints]) - [Description]
- created_at (timestamptz)
- updated_at (timestamptz)

**Relationships:**
- **Belongs to:** User (profiles via user_id)
- **Has many:** [Related entities via foreign key]
- **Related to:** [Junction table relationships]

**RLS Policies:**
- SELECT: Users can view their own records
- INSERT: Users can create their own records
- UPDATE: Users can update their own records
- DELETE: Users can delete their own records

**Indexes:**
- user_id (for user lookups)
- [other_field]_idx (for [purpose])

**Migrations:**
- `[timestamp]_[migration_name].sql` - Initial table creation

**Seed Data:**
- Per-user seed data creates [X] sample records
- Located in: `seed_user_data()` function
```

---

## Step 4: Update README.md

### Add Feature to Features List

```markdown
## Features

[Existing features...]

- **[Feature Name]**: [Brief description of what it does]
```

### Update Setup Instructions (If Needed)

**If feature requires additional setup:**

```markdown
## Setup

[Existing setup...]

5. **Configure [Feature]**
   ```bash
   # Additional setup command if needed
   ```
```

---

## Step 5: Update Troubleshooting Documentation

### Add to SYSTEM_REFERENCE.md Troubleshooting Section

**Document known issues discovered during implementation:**

```markdown
### [Feature Name] Issues

#### Issue: [Symptom]

**Cause:** [Root cause]

**Solution:**
```bash
# Fix command or steps
```

**Prevention:** [How to avoid]
```

### Common Issues from Development

**Extract from Phase 4 test results and add:**

- Issues encountered
- Solutions that worked
- Debugging steps
- Prevention tips

---

## Step 6: Create Feature Documentation (Optional)

### Create User-Facing Documentation

**File:** `docs/features/[feature-name].md`

```markdown
# [Feature Name] Guide

## Overview

[What the feature does and why it's useful]

## Getting Started

### Accessing the Feature

1. Navigate to [path]
2. [Step 2]

### Basic Usage

**To [action]:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**To [another action]:**
[Steps...]

## Examples

### Example 1: [Scenario]

[Step-by-step with screenshots or descriptions]

### Example 2: [Another Scenario]

[Steps...]

## Tips and Tricks

- Tip 1
- Tip 2

## Troubleshooting

### Problem: [Issue]
**Solution:** [Fix]

## FAQ

**Q: [Question]?**
A: [Answer]

## Related Features

- [Feature A] - [How they relate]
- [Feature B] - [How they relate]
```

---

## Step 7: Update Guide Index (If New Patterns)

### If Feature Introduces New Patterns

**Update `.clinefiles/guide-index.md`:**

```markdown
### [category]/[new-guide].md
**Read this for:** [When to use this guide]
**Summary:** [Brief description]
**Location:** `.clinefiles/[path]`
```

**Add to Common Task Scenarios:**

```markdown
### "Implementing [feature type]"
**Read these guides:**
1. `path/to/relevant/guide.md` - [What it covers]
2. `path/to/another/guide.md` - [What it covers]
```

---

## Step 8: Clean Up Temporary Files

### Archive or Remove

- [ ] Delete FEATURE_PLAN.md (or move to archive)
- [ ] Archive FEATURE_TEST_RESULTS.md
- [ ] Remove any temporary test files
- [ ] Clean up any debugging code
- [ ] Remove console.log statements

---

## Step 9: Final Verification

### Documentation Completeness Check

**PROJECT_REQUIREMENTS.md:**
- [ ] Feature added to features list
- [ ] New entities documented (if applicable)
- [ ] Acceptance criteria listed
- [ ] Implementation status marked complete

**SYSTEM_REFERENCE.md:**
- [ ] Architecture updated
- [ ] Database schema documented
- [ ] API endpoints listed (if applicable)
- [ ] Agent tools documented (if applicable)
- [ ] Integration points explained
- [ ] Troubleshooting updated

**DATABASE_SCHEMA.md:**
- [ ] All new tables documented
- [ ] Relationships clearly explained
- [ ] RLS policies described
- [ ] Migrations referenced

**README.md:**
- [ ] Feature list updated
- [ ] Setup instructions current
- [ ] All features mentioned work

### Cross-Reference Verification

**Verify consistency across docs:**
- [ ] Entity names match across all files
- [ ] Table names consistent
- [ ] Route paths match between docs and code
- [ ] Tool names match between docs and code

---

## Step 10: Update WORKFLOW_CHECKPOINT.md

### Mark Feature Complete

```markdown
## ✅ Completed Features

### [Feature Name]
- **Completed:** [Date]
- **Complexity:** Simple | Moderate | Complex
- **Phases:** [0, 1, 2, 4, 5]
- **Implementation:**
  - Database: [Table names]
  - Frontend: [Routes]
  - Agent: [Tools] (if applicable)

**Key Decisions:**
- [Decision 1]
- [Decision 2]

**Lessons Learned:**
- [Lesson 1]
- [Lesson 2]

**Future Enhancements:**
- [Idea 1]
- [Idea 2]
```

---

## Common Issues and Solutions

### Issue 1: Documentation out of sync

**Symptom:** Docs don't match implementation

**Solution:** 
- Review all changed files
- Update docs to match actual code
- Test documented examples

### Issue 2: Missing integration points

**Symptom:** Unclear how services connect

**Solution:**
- Draw data flow diagram
- Document each boundary
- Include code file references

### Issue 3: Troubleshooting section incomplete

**Symptom:** Known issues not documented

**Solution:**
- Review Phase 4 test results
- Add all encountered issues
- Include solutions that worked

---

## Phase 5 Completion Checklist

### Documentation Updates
- [ ] PROJECT_REQUIREMENTS.md updated
- [ ] SYSTEM_REFERENCE.md updated
- [ ] DATABASE_SCHEMA.md updated (if Phase 1)
- [ ] README.md updated
- [ ] Troubleshooting guide updated
- [ ] Guide index updated (if new patterns)

### Feature Documentation
- [ ] User guide created (optional)
- [ ] Examples provided
- [ ] Common issues documented
- [ ] FAQ added (if needed)

### Cleanup
- [ ] Temporary files removed
- [ ] Debug code removed
- [ ] Console logs removed
- [ ] Code comments updated

### Verification
- [ ] All docs reviewed for accuracy
- [ ] Cross-references checked
- [ ] Examples tested
- [ ] Documentation complete

### Workflow Tracking
- [ ] WORKFLOW_CHECKPOINT.md updated
- [ ] Feature marked complete
- [ ] Lessons learned documented

**Documentation is complete when future developers can understand and modify the feature using only the docs.**

---

## Feature Complete!

**Congratulations! The feature is complete when:**

✅ All phases executed
✅ All tests passing
✅ All documentation updated
✅ No outstanding issues
✅ Code reviewed and clean
✅ Ready for users

**Next steps:**
- Deploy to production (if applicable)
- Monitor feature usage
- Gather user feedback
- Plan future enhancements
- Start next feature!

---

## Return to Workflow

**Return to:** [new-feature.md](../new-feature.md) to mark workflow complete or start next feature
